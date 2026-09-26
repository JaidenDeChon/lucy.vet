#!/usr/bin/env python3
"""Queue, ledger and detail guard for the copy-humanizer agent.

The agent rewrites the reader-facing text of one file at a time with the
humanizer skill. This script picks the file, checks that the rewrite kept
every detail, and records the file as done.

    python3 scripts/humanize_copy.py next                # print the next item to humanize
    python3 scripts/humanize_copy.py status              # counts: done, stale, remaining
    python3 scripts/humanize_copy.py next --marketing    # next item in the marketing sweep
    python3 scripts/humanize_copy.py status --marketing
    python3 scripts/humanize_copy.py check FILE          # compare FILE with its HEAD version
    python3 scripts/humanize_copy.py record FILE         # mark FILE as humanized

Paths are relative to the repo root, e.g. "content/0.index.yml" or
"app/components/AppHeader.vue".

The default queue puts the site chrome and the Vue files that carry copy on
the home and pricing pages first, so a button or link has its final name
before the content that refers to it is rewritten. Then come the three
marketing content files, the auth pages and any other page or component that
appears later, and last the docs in content/1.docs (sample docs from the
Nuxt UI SaaS template, live at /docs). The marketing sweep (`--marketing`)
is the same queue without the docs and the auth pages.

Never queued: the demo components that replicate the product's screens
(their labels mirror app.lucy.vet), template leftovers that nothing renders,
components with no copy, layouts, .navigation.yml files, and the share-card
source in tools/share-preview (it mirrors the home page hero and is edited in
the same run as content/0.index.yml).

What `check` does, by file type:

- .yml content: every YAML line stays byte for byte except the value of a
  key listed in YAML_PROSE (the copy). Placeholder text (lorem ipsum, or the
  word "placeholder") is locked, and so is every other value in the same list
  item. The new file must parse (checked with Bun.YAML when Bun is present).
- .md content: frontmatter stays byte for byte except its `description`;
  headings, code fences, ::code-preview blocks, component props and slot
  markers stay byte for byte.
- .vue, .ts and .html: every string literal and template text node that reads
  as copy is masked, then the rest of the file (the code) must be unchanged.
  <style> must be unchanged too. Strings passed to useSeoMeta as a title,
  titleTemplate or image stay locked. Replica files (REPLICA_UI) only unlock
  their screen-reader text.

For every type, `check` fails if the copy lost or gained a link, a number, a
quotation, inline code, an MDC attribute or a claim word (security,
compliance, pricing offers, release status, legal wording), or if a file that
mirrors this one (MIRRORS) has drifted from it. It warns when a capitalised
word or italic span vanished, or when two values that were identical at HEAD
now differ.

`check` exits 1 on a hard failure and 0 otherwise; warnings alone exit 0.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / ".claude" / "humanized-copy.json"

# ---------------------------------------------------------------- queue ---

# Site chrome and the Vue files that put copy on the marketing pages, in
# sweep order. Control names settle here before the content refers to them.
UI_FIRST = [
    "app/components/AppHeader.vue",
    "app/components/AppFooter.vue",
    "app/components/AppLogo.vue",
    "app/pages/index.vue",
    "app/components/demo/DemoClinicShowcase.vue",
    "app/components/demo/DemoCalendarPreview.vue",
    "app/pages/pricing.vue",
    "app/app.vue",
    "app/error.vue",
]
MARKETING_CONTENT = [
    "content/0.index.yml",
    "content/1.features.yml",
    "content/2.pricing.yml",
]
# Stub and template auth pages: reachable, but not part of the pitch.
AUTH_PAGES = [
    "app/pages/get-started.vue",
    "app/pages/sign-up.vue",
    "app/pages/login.vue",
    "app/pages/signup.vue",
]
DOCS_DIR = "content/1.docs"

# Never queued. Demo replicas copy the product's own labels; the rest carry
# no copy or are template leftovers nothing renders.
SKIP = {
    "app/components/demo/DemoBillingLedger.vue",
    "app/components/demo/DemoCanvas.vue",
    "app/components/demo/DemoInventoryTable.vue",
    "app/components/demo/DemoPatientPage.vue",
    "app/components/demo/DemoPatientsTable.vue",
    "app/components/demo/DemoPatientWorkspace.vue",
    "app/components/demo/DemoUpcomingAppointments.vue",
    "app/components/HeroBackground.vue",
    "app/components/ImagePlaceholder.vue",
    "app/components/PromotionalVideo.vue",
    "app/components/StarsBg.vue",
    "app/components/TemplateMenu.vue",
    "app/components/content/PictureAndText.vue",
    "app/components/content/Pictures.vue",
    "app/components/OgImage/OgImageSaas.vue",
    "app/pages/blog.vue",
    "app/pages/docs/index.vue",
    "app/pages/docs/[...slug].vue",
    "app/pages/features.vue",
}
SKIP_DIRS = ("app/layouts/", "app/components/demo/")  # new demo files are replicas until listed
SKIP_NAMES = {".navigation.yml"}

# Files whose strings mirror the product. Only screen-reader text may change.
REPLICA_UI = {"app/components/demo/DemoCalendarPreview.vue"}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def extra_items(listed: set[str]) -> list[Path]:
    """Pages, components and content added since the lists above were written."""
    found = list((ROOT / "app").rglob("*.vue")) + list((ROOT / "content").rglob("*.yml"))
    out = []
    for p in sorted(found, key=rel):
        r = rel(p)
        if (r in listed or r in SKIP or p.name in SKIP_NAMES or r.startswith(DOCS_DIR)
                or r.startswith(SKIP_DIRS)):
            continue
        out.append(p)
    return out


def all_items(marketing: bool = False) -> list[Path]:
    names = UI_FIRST + MARKETING_CONTENT + ([] if marketing else AUTH_PAGES)
    items = [ROOT / n for n in names if (ROOT / n).is_file()]
    items += extra_items(set(UI_FIRST + MARKETING_CONTENT + AUTH_PAGES))
    if not marketing:
        docs = [p for p in (ROOT / DOCS_DIR).rglob("*.md")]
        items += sorted(docs, key=lambda p: rel(p).lower())
    return items


def load_ledger() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(marketing: bool = False) -> tuple[list[Path], list[Path], list[Path]]:
    """Split items into (never done, changed since done, done and unchanged)."""
    ledger = load_ledger()
    new, stale, done = [], [], []
    for item in all_items(marketing):
        entry = ledger.get(rel(item))
        if entry is None:
            new.append(item)
        elif entry.get("sha256") != sha(item):
            stale.append(item)
        else:
            done.append(item)
    return new, stale, done


def cmd_next(marketing: bool) -> int:
    new, stale, _ = classify(marketing)
    queue = new + stale
    print(rel(queue[0]) if queue else "ALL DONE")
    return 0


def cmd_status(marketing: bool) -> int:
    new, stale, done = classify(marketing)
    print(f"done: {len(done)}  never humanized: {len(new)}  changed since humanized: {len(stale)}")
    return 0


def cmd_record(path: Path) -> int:
    ledger = load_ledger()
    ledger[rel(path)] = {
        "humanized_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256": sha(path),
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(dict(sorted(ledger.items())), indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(f"recorded {rel(path)}")
    return 0


# ---------------------------------------------------------------- facts ---

URL_RE = re.compile(r"\]\([^)]+\)|<https?://[^>]+>|https?://[^\s)\"'<>]+")
NUMBER_RE = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
QUOTE_RE = re.compile(r"\"([^\"\n]{3,})\"|“([^”\n]{3,})”")
ITALIC_RE = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])|(?<!\w)_([^_\n]+)_(?!\w)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
MDC_ATTR_RE = re.compile(r"\]\{[^}\n]*\}")
# Capitalised words mid-sentence: likely names, product terms and places.
CAP_RE = re.compile(r"(?<=[\w,;:)\]] )[A-Z][A-Za-z0-9'’.-]*[A-Za-z0-9]\b")
# Words that carry a security, compliance, pricing, release-status or legal
# claim. Their count must not change: a rewrite may move them, not add or
# drop them. (Stems, so "secure" and "securely" count as one.)
CLAIM_TERMS = [
    r"secur\w*", r"hipaa", r"soc ?2", r"pci\b", r"gdpr", r"complian\w*", r"encrypt\w*",
    r"privacy", r"private", r"backups?", r"audit\w*", r"certif\w*", r"guarante\w*",
    r"uptime", r"free", r"unlimited", r"trial", r"refund\w*", r"cancel\w*",
    r"(?:pre-)?alpha", r"beta", r"automat\w*", r"real[- ]time", r"terms of service",
    r"agree\w*", r"©", r"copyright",
]
CLAIM_RE = re.compile(r"(?i)(?<![\w-])(" + "|".join(CLAIM_TERMS) + r")(?![\w-])")


def claim_key(word: str) -> str:
    low = word.lower()
    for term in CLAIM_TERMS:
        if re.fullmatch(term, low):
            return term.replace(r"\w*", "…").replace("\\b", "").replace("?", "")
    return low


def facts(prose: str) -> dict[str, Counter]:
    italics = Counter(a or b for a, b in ITALIC_RE.findall(prose))
    quotes = Counter(a or b for a, b in QUOTE_RE.findall(prose))
    bare = INLINE_CODE_RE.sub(" ", URL_RE.sub(" ", prose))
    return {
        "links": Counter(URL_RE.findall(prose)),
        "inline code": Counter(INLINE_CODE_RE.findall(prose)),
        "MDC attributes": Counter(MDC_ATTR_RE.findall(prose)),
        "numbers": Counter(n.replace(",", "") for n in NUMBER_RE.findall(bare)),
        "quotes": quotes,
        "claim words": Counter(claim_key(w) for w in CLAIM_RE.findall(bare)),
        "italics": italics,
        "capitalised": Counter(CAP_RE.findall(bare)),
    }


HARD_KINDS = ("links", "inline code", "MDC attributes", "numbers", "quotes", "claim words")


def show(counter: Counter) -> str:
    return ", ".join(f"{k!r}" + (f" x{v}" if v > 1 else "") for k, v in sorted(counter.items()))


def compare_facts(old_prose: str, new_prose: str, errors: list[str], warnings: list[str]) -> None:
    before, after = facts(old_prose), facts(new_prose)
    for kind in HARD_KINDS:
        lost, gained = before[kind] - after[kind], after[kind] - before[kind]
        if lost:
            errors.append(f"{kind} lost: {show(lost)}")
        if gained:
            errors.append(f"{kind} added: {show(gained)}")
    for kind in ("italics", "capitalised"):
        lost = before[kind] - after[kind]
        # A word may survive in a new position or case, so warn only when it
        # is gone entirely. Review, not failure.
        lost = Counter({k: v for k, v in lost.items() if k.lower() not in new_prose.lower()})
        if lost:
            warnings.append(f"{kind} no longer present: {show(lost)}")


# ----------------------------------------------------------------- yaml ---

# Keys whose values are copy, as dotted paths with [] for any list item.
# Everything else (ids, links, icons, colours, prices, plan names, the hero
# headline and badge, SEO titles, testimonials, plan feature lists) is locked.
YAML_PROSE = {
    "title", "description", "seo.description",
    "hero.links[].label",
    "sections[].title", "sections[].description",
    "sections[].features[].name", "sections[].features[].description",
    "demo.title",
    "features.title", "features.description",
    "features.items[].title", "features.items[].description",
    "cta.title", "cta.description", "cta.links[].label",
    "plans[].description", "plans[].button.label",
    "logos.title",
    "faq.title", "faq.description", "faq.items[].label", "faq.items[].content",
}
# Per-file exceptions. The home page headline is the brand line: it holds an
# MDC span, and the share card in tools/share-preview repeats it.
YAML_LOCKED = {"content/0.index.yml": {"title"}}

LOREM = ("lorem ipsum dolor amet consectetur adipisicing culpa pariatur commodo aliqua tempor "
         "nisi deserunt cillum nostrud aliquip reprehenderit proident veniam occaecat eiusmod "
         "irure mollit officia cupidatat duis voluptate incididunt ullamco labore consequat minim "
         "magna elit enim").split()
PLACEHOLDER_RE = re.compile(r"(?i)\bplaceholder\b|\b(?:" + "|".join(LOREM) + r")\b.*\b(?:"
                            + "|".join(LOREM) + r")\b")
KEY_RE = re.compile(r"^(\"[^\"]*\"|'[^']*'|[^\s\"'#:-][^:#]*?|-[^\s][^:#]*?):(?:\s+(.*?))?\s*$")
BLOCK_SCALAR_RE = re.compile(r"^[|>][+-]?\d*$")


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def yaml_entries(text: str) -> list[dict]:
    """One entry per line: {line, path, norm, scope, prefix, value, block, owner}.

    `path` is the dotted key path with list indices, `norm` the same with []
    for every index, `scope` the path of the nearest enclosing list item.
    `value` is set on lines that hold a scalar; continuation lines of a block
    or multi-line scalar point at their owner entry.
    """
    entries: list[dict] = []
    stack: list[tuple[int, str, bool]] = []  # (indent, name, is list item)
    counters: dict[str, int] = {}
    owner: dict | None = None

    def path() -> str:
        out = ""
        for _, name, item in stack:
            out += name if item else ("." if out else "") + name
        return out

    def scope() -> str:
        for i in range(len(stack) - 1, -1, -1):
            if stack[i][2]:
                return path_upto(i)
        return ""

    def path_upto(i: int) -> str:
        out = ""
        for _, name, item in stack[: i + 1]:
            out += name if item else ("." if out else "") + name
        return out

    def key_entry(line: str, indent: int, body: str, m: re.Match) -> dict:
        while stack and stack[-1][0] >= indent:
            stack.pop()
        stack.append((indent, unquote(m.group(1).strip()), False))
        value = m.group(2) or ""
        p = path()
        prefix = line[: len(line) - len(body)] + body[: body.index(":") + 1] + (" " if value else "")
        return {"line": line, "path": p, "norm": re.sub(r"\[\d+\]", "[]", p), "scope": scope(),
                "prefix": prefix, "value": value if value and not BLOCK_SCALAR_RE.match(value) else None,
                "block": bool(value and BLOCK_SCALAR_RE.match(value)), "indent": indent}

    for line in text.splitlines():
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if owner is not None and stripped and indent > owner["indent"] and (
                owner["block"] or not (stripped.startswith("- ") or KEY_RE.match(stripped))):
            entries.append({"line": line, "owner": owner})
            continue
        if owner is not None and owner["block"] and not stripped:
            entries.append({"line": line, "owner": owner})
            continue
        owner = None
        if not stripped or stripped.startswith("#") or stripped in ("---", "..."):
            entries.append({"line": line})
            continue
        if stripped == "-" or stripped.startswith("- "):
            while stack and (stack[-1][0] > indent or (stack[-1][2] and stack[-1][0] >= indent)):
                stack.pop()
            parent = path()
            counters[parent] = counters.get(parent, -1) + 1
            stack.append((indent, f"[{counters[parent]}]", True))
            rest = stripped[1:].lstrip()
            inner = indent + (len(stripped) - len(rest))
            m = KEY_RE.match(rest) if rest else None
            if m:
                e = key_entry(line, inner, rest, m)
                owner = e
                entries.append(e)
            elif rest:
                p = path()
                e = {"line": line, "path": p, "norm": re.sub(r"\[\d+\]", "[]", p), "scope": p,
                     "prefix": line[:inner], "value": rest, "block": False, "indent": indent}
                owner = e
                entries.append(e)
            else:
                entries.append({"line": line})
            continue
        m = KEY_RE.match(stripped)
        if m:
            e = key_entry(line, indent, stripped, m)
            owner = e
            entries.append(e)
            continue
        entries.append({"line": line})
    return entries


def yaml_prose_paths(page: str) -> set[str]:
    return YAML_PROSE - YAML_LOCKED.get(page, set())


def split_yaml(text: str, page: str) -> tuple[list[str], str, dict[str, str]]:
    """Return (locked lines, editable prose, {path: copy value})."""
    entries = yaml_entries(text)
    prose_paths = yaml_prose_paths(page)
    placeholder_scopes = {e["scope"] for e in entries
                          if e.get("value") and e.get("scope") and PLACEHOLDER_RE.search(e["value"])}
    locked: list[str] = []
    prose: list[str] = []
    values: dict[str, str] = {}

    def editable(e: dict) -> bool:
        if e.get("norm") not in prose_paths:
            return False
        if e.get("scope") and e["scope"] in placeholder_scopes:
            return False
        if e.get("value") and PLACEHOLDER_RE.search(e["value"]):
            return False
        return bool(e.get("value") or e.get("block"))

    for e in entries:
        target = e.get("owner") or e
        if "owner" in e:
            if editable(target):
                prose.append(e["line"].strip())
                values[target["path"]] = (values.get(target["path"], "") + " " + e["line"].strip()).strip()
            else:
                locked.append(e["line"])
            continue
        if editable(e):
            locked.append(e["prefix"].rstrip() + (" |" if e["block"] else ""))
            if e.get("value"):
                prose.append(unquote(e["value"]))
                values[e["path"]] = unquote(e["value"])
            else:
                values[e["path"]] = ""
        else:
            locked.append(e["line"])
    return locked, "\n".join(prose), values


def yaml_parses(text: str) -> str | None:
    """Parse with Bun.YAML. Returns an error, "" when it parsed, None if it could not run."""
    bun = shutil.which("bun")
    if not bun:
        return None
    js = ("const t = await Bun.stdin.text();"
          "if (!Bun.YAML) { console.log('NO_YAML'); process.exit(0) }"
          "try { Bun.YAML.parse(t); console.log('OK') } catch (e) { console.log(String(e.message)) }")
    try:
        out = subprocess.run([bun, "-e", js], input=text, capture_output=True, text=True,
                             cwd=ROOT, timeout=60).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if out == "NO_YAML":
        return None
    return "" if out == "OK" else out or "no output from bun"


def check_yaml(page: str, old: str, new: str, errors: list[str], warnings: list[str]) -> None:
    old_locked, old_prose, old_values = split_yaml(old, page)
    new_locked, new_prose, new_values = split_yaml(new, page)
    if old_locked != new_locked:
        diff = [l for l in difflib.unified_diff(old_locked, new_locked, lineterm="", n=0)
                if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
        errors.append("keys, structure or locked values changed (only the values of "
                      + ", ".join(sorted(yaml_prose_paths(page)))
                      + " may change, and not when they hold placeholder text):"
                      + "".join(f"\n    {l}" for l in diff[:20]))
    for p, v in new_values.items():
        if not v.strip():
            errors.append(f"{p} is empty; content.config.ts requires a non-empty string")
    for e in yaml_entries(new):
        raw = e.get("value")
        if (raw and e.get("path") in new_values and raw[0] not in "'\""
                and re.search(r": | #", raw)):
            errors.append(f"{e['path']}: a value holding ': ' or ' #' must be double-quoted")
    parsed = yaml_parses(new)
    if parsed is None:
        warnings.append("could not parse-check the YAML (needs Bun 1.2.21+ on PATH); "
                        "run `bun run build` to be sure it still loads")
    elif parsed:
        errors.append(f"the file no longer parses as YAML: {parsed}")
    # Values that were identical at HEAD (a hero description and its SEO
    # copy, a feature repeated in two lists) usually should stay identical.
    groups: dict[str, list[str]] = {}
    for p, v in old_values.items():
        groups.setdefault(v, []).append(p)
    for paths in groups.values():
        if len(paths) > 1 and len({new_values.get(p) for p in paths}) > 1:
            warnings.append("these values were identical at HEAD and now differ; confirm that is "
                            "intended: " + ", ".join(paths))
    compare_facts(old_prose, new_prose, errors, warnings)


# ------------------------------------------------------------- markdown ---

DOC_PROSE_PROPS = {"label", "title", "description"}


def split_markdown(text: str) -> tuple[list[str], str]:
    """Return (locked lines, editable prose) for an MDC page."""
    locked: list[str] = []
    prose: list[str] = []
    m = re.match(r"\A---\n(.*?\n)---\n", text, re.DOTALL)
    if m:
        locked.append("---")
        for line in m.group(1).splitlines():
            dm = re.match(r"^(description:)\s*(.*)$", line)
            if dm:
                locked.append(dm.group(1))
                prose.append(unquote(dm.group(2).strip()))
            else:
                locked.append(line)
        locked.append("---")
        text = text[m.end():]

    in_code = False
    preview_depth = 0  # colon count of an open ::code-preview, 0 when none
    in_props = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            locked.append(line)
            continue
        if in_code:
            locked.append(line)
            continue
        if preview_depth:
            locked.append(line)
            if re.fullmatch(r":+", stripped) and len(stripped) == preview_depth:
                preview_depth = 0
            continue
        opener = re.match(r"^(:{2,})([\w-]+)", stripped)
        if opener:
            if opener.group(2) == "code-preview":
                preview_depth = len(opener.group(1))
            locked.append(line)
            continue
        if re.fullmatch(r":{2,}", stripped):
            in_props = False
            locked.append(line)
            continue
        if stripped == "---":
            # A component's props block (the page's frontmatter is gone).
            in_props = not in_props
            locked.append(line)
            continue
        if in_props:
            pm = re.match(r"^(\s*)([\w-]+):\s*(.*)$", line)
            if pm and pm.group(2) in DOC_PROSE_PROPS:
                locked.append(f"{pm.group(1)}{pm.group(2)}:")
                prose.append(unquote(pm.group(3).strip()))
            else:
                locked.append(line)
            continue
        if re.fullmatch(r"#[\w-]+", stripped):  # slot marker such as #code
            locked.append(line)
            continue
        if stripped.startswith("#") or re.match(r"^\|?\s*:?-{3,}", stripped):
            locked.append(line)
            continue
        prose.append(line)
    return locked, "\n".join(prose)


def check_markdown(old: str, new: str, errors: list[str], warnings: list[str]) -> None:
    old_locked, old_prose = split_markdown(old)
    new_locked, new_prose = split_markdown(new)
    if old_locked != new_locked:
        diff = [l for l in difflib.unified_diff(old_locked, new_locked, lineterm="", n=0)
                if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
        errors.append("frontmatter (other than description), headings, code, ::code-preview "
                      "blocks, component props or slot markers changed:"
                      + ("".join(f"\n    {l}" for l in diff[:20]) or " order differs"))
    compare_facts(old_prose, new_prose, errors, warnings)


# ----------------------------------------------------------------- code ---

# Comments come first so an apostrophe in a comment never opens a string.
STRING_RE = re.compile(r"//[^\n]*|/\*.*?\*/|'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"|`(?:[^`\\]|\\.)*`", re.S)
# Static attributes whose values a reader sees or hears.
TEXT_ATTR_RE = re.compile(r"(?<![:@\w-])((?:aria-label|aria-description|title|placeholder|alt|label|description)=)\"([^\"]*)\"")
TEXT_NODE_RE = re.compile(r">([^<>\"=]*)<")
MUSTACHE_RE = re.compile(r"\{\{.*?\}\}", re.S)
BOUND_ATTR_RE = re.compile(r"((?:[:@#]|v-)[\w:.-]*=)\"([^\"]*)\"")
SR_ONLY_RE = re.compile(r"(<(\w+)\b[^>]*\bclass=\"[^\"]*\bsr-only\b[^\"]*\"[^>]*>)([^<]*)(</\2>)")
# In useSeoMeta, only the descriptions are copy. Titles are names the owner
# chose for search and browser tabs, and the rest are URLs or settings.
SEO_CALL_RE = re.compile(r"useSeoMeta\(\{.*?\}\)", re.S)
SEO_LOCKED_KEY_RE = re.compile(r"\b(?!(?:description|ogDescription|twitterDescription)\b)\w+\s*:\s*$")

# Single-word strings that are code or names, not copy: keyboard keys,
# provider names and the product's own names.
CODE_WORDS = {"Enter", "Escape", "Tab", "Home", "End", "Space", "Backspace", "Delete",
              "PageUp", "PageDown", "Shift", "Control", "Alt", "Meta", "Root",
              "Google", "GitHub", "Lucy", "Lucero"}


def mask_strings(text: str, sink: list[str]) -> str:
    """Mask the string literals that read as copy: they hold a space or an
    ellipsis, or are one capitalised word. Ids, class names, keys and paths
    stay visible to the check. Each masked string is appended to `sink`."""
    protected = set()
    for call in SEO_CALL_RE.finditer(text):
        for s in STRING_RE.finditer(call.group(0)):
            if s.group(0)[0] in "'\"`" and SEO_LOCKED_KEY_RE.search(call.group(0)[: s.start()]):
                protected.add(call.start() + s.start())

    def one(m: re.Match) -> str:
        if m.group(0).startswith("/") or m.start() in protected:
            return m.group(0)
        body = m.group(0)[1:-1]
        words = re.sub(r"\$\{[^}]*\}", "", body) if m.group(0)[0] == "`" else body
        bare = words.strip()
        prose = (re.search(r"[A-Za-z]", words) and (" " in bare or "…" in words or "(" in bare)
                 or (re.fullmatch(r"[A-Z][a-z]+", bare) and bare not in CODE_WORDS))
        if not prose:
            return m.group(0)
        sink.append(words)
        if m.group(0)[0] == "`":
            # Keep the ${...} expressions visible: they are code.
            return "`" + "§".join(re.findall(r"\$\{[^}]*\}", body)) + "§S§`"
        return "§S§"
    return STRING_RE.sub(one, text)


def mask_text_node(node: str, sink: list[str]) -> str:
    """Mask the words in a template text node. Its {{ }} expressions are code,
    so they must survive in the same order; the words around them may move."""
    words = re.sub(r"\{\{.*?\}\}", "", node, flags=re.S)
    if not re.search(r"[A-Za-z]", words) and not ("{{" in node and words.strip()):
        return node
    sink.append(words)
    return "§T§" + "".join(re.findall(r"\{\{.*?\}\}", node, flags=re.S))


def mask_markup(block: str, sink: list[str]) -> str:
    b = MUSTACHE_RE.sub(lambda m: mask_strings(m.group(0), sink), block)
    b = BOUND_ATTR_RE.sub(lambda m: m.group(1) + '"' + mask_strings(m.group(2), sink) + '"', b)

    def attr(m: re.Match) -> str:
        sink.append(m.group(2))
        return m.group(1) + '"§A§"'
    b = TEXT_ATTR_RE.sub(attr, b)
    return TEXT_NODE_RE.sub(lambda m: ">" + mask_text_node(m.group(1), sink) + "<", b)


def mask_replica(text: str, sink: list[str]) -> str:
    """For a product replica, only screen-reader text is copy."""
    def one(m: re.Match) -> str:
        sink.append(m.group(3))
        return m.group(1) + "§T§" + m.group(4)
    return SR_ONLY_RE.sub(one, text)


STYLE_RE = re.compile(r"<style\b.*?</style>", re.S)


def mask_code(text: str, kind: str, sink: list[str]) -> str:
    """Blank out everything a copy edit may change, so what is left is code."""
    if kind == "replica":
        return mask_replica(text, sink)
    if kind == "ts":
        return mask_strings(text, sink)
    if kind == "html":
        # Styles are compared on their own; keep CSS out of the markup masks.
        styles: list[str] = []

        def park(m: re.Match) -> str:
            styles.append(m.group(0))
            return f"§STYLE{len(styles) - 1}§"
        body = STYLE_RE.sub(park, text)
        body = re.sub(r"(<script\b[^>]*>)(.*?)(</script>)",
                      lambda m: m.group(1) + mask_strings(m.group(2), sink) + m.group(3), body, flags=re.S)
        return mask_markup(body, sink)
    out = []
    # Split into top-level blocks; <template> is masked as markup, <script> as code.
    for block in re.split(r"(?=^<(?:template|script|style)\b)", text, flags=re.M):
        if block.startswith("<script"):
            out.append(mask_strings(block, sink))
        elif block.startswith("<template"):
            out.append(mask_markup(block, sink))
        else:
            out.append(block)
    return "".join(out)


def code_kind(page: str) -> str:
    if page in REPLICA_UI:
        return "replica"
    return {".vue": "vue", ".html": "html"}.get(Path(page).suffix, "ts")


def check_code(page: str, old: str, new: str, errors: list[str], warnings: list[str]) -> None:
    kind = code_kind(page)
    if kind != "ts":
        styles = (lambda t: STYLE_RE.findall(t))
        if styles(old) != styles(new):
            errors.append("<style> changed; only user-facing text may change")
    old_copy: list[str] = []
    new_copy: list[str] = []
    old_code = mask_code(old, kind, old_copy).splitlines()
    new_code = mask_code(new, kind, new_copy).splitlines()
    if old_code != new_code:
        diff = [l for l in difflib.unified_diff(old_code, new_code, lineterm="", n=0)
                if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
        what = ("screen-reader text (this file replicates the product's screens)" if kind == "replica"
                else "string literals and template text; useSeoMeta titles and image paths "
                     "count as code")
        errors.append(f"code changed outside {what} (only user-facing text may change):"
                      + "".join(f"\n    {l}" for l in diff[:20]))
    compare_facts("\n".join(old_copy), "\n".join(new_copy), errors, warnings)


# -------------------------------------------------------------- mirrors ---

def _yaml_value(text: str, page: str, path: str) -> str | None:
    for e in yaml_entries(text):
        if e.get("path") == path and e.get("value") is not None:
            return unquote(e["value"])
    return None


def _norm(text: str | None) -> str | None:
    if text is None:
        return None
    text = re.sub(r"\[([^\]]*)\]\{[^}]*\}", r"\1", text)  # MDC span -> its words
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _html_part(pattern: str):
    rx = re.compile(pattern, re.S)
    return lambda text: (m.group(1) if (m := rx.search(text)) else None)


# (file, how to read the value, file that mirrors it, how to read it there, what it is)
INDEX = "content/0.index.yml"
SHARE = "tools/share-preview/index.html"
MIRRORS = [
    (INDEX, lambda t: _yaml_value(t, INDEX, "description"),
     SHARE, _html_part(r"<p class=\"description\">(.*?)</p>"), "hero description on the share card"),
    (INDEX, lambda t: _yaml_value(t, INDEX, "title"),
     SHARE, _html_part(r"<h1>(.*?)</h1>"), "hero headline on the share card"),
    (INDEX, lambda t: _yaml_value(t, INDEX, "hero.badge.label"),
     SHARE, _html_part(r"<div class=\"badge\">(.*?)</div>"), "hero badge on the share card"),
    (INDEX, lambda t: _yaml_value(t, INDEX, "demo.title"),
     "app/pages/index.vue", _html_part(r"demo\?\.title \?\?\s*'([^']*)'"),
     "demo section title and its fallback in app/pages/index.vue"),
]


def head_text(page: str) -> str | None:
    try:
        return subprocess.run(["git", "show", f"HEAD:{page}"], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout
    except subprocess.CalledProcessError:
        return None


def work_text(page: str) -> str | None:
    p = ROOT / page
    return p.read_text(encoding="utf-8") if p.is_file() else None


def check_mirrors(page: str, errors: list[str], notes: list[str]) -> None:
    for src, read_src, dst, read_dst, what in MIRRORS:
        if page not in (src, dst):
            continue
        old_src, old_dst = head_text(src), head_text(dst)
        new_src, new_dst = work_text(src), work_text(dst)
        if None in (old_src, old_dst, new_src, new_dst):
            continue
        was = _norm(read_src(old_src)) == _norm(read_dst(old_dst))
        now_a, now_b = _norm(read_src(new_src)), _norm(read_dst(new_dst))
        if was and now_a != now_b:
            errors.append(f"{what}: {src} and {dst} matched at HEAD and now differ; "
                          f"change both in the same commit")
        elif dst == SHARE and _norm(read_dst(old_dst)) != now_b:
            notes.append(f"{what} changed: public/social-thumbnail-v*.png is now stale. "
                         "Regenerate it per tools/share-preview/README.md, or report it.")


# ---------------------------------------------------------------- check ---

def cmd_check(path: Path) -> int:
    page = rel(path)
    old = head_text(page)
    if old is None:
        print(f"{page} is not in HEAD; commit it before humanizing.")
        return 1
    new = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    check_mirrors(page, errors, notes)
    if old == new and not errors:
        for n in notes:
            print(f"NOTE {n}")
        print("unchanged")
        return 0
    suffix = path.suffix
    if old != new:
        if suffix in (".yml", ".yaml"):
            check_yaml(page, old, new, errors, warnings)
        elif suffix == ".md":
            check_markdown(old, new, errors, warnings)
        elif suffix in (".vue", ".ts", ".html"):
            check_code(page, old, new, errors, warnings)
        else:
            errors.append(f"no copy rules for {suffix} files")

    for w in warnings:
        print(f"WARNING {w}")
    for e in errors:
        print(f"ERROR {e}")
    for n in notes:
        print(f"NOTE {n}")
    if errors:
        return 1
    print("ok" + (" (review the warnings above)" if warnings else "")
          + " (now run: bun run lint && bun run typecheck)")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in {"next", "status", "check", "record"}:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd in ("next", "status"):
        marketing = "--marketing" in argv[2:]
        return cmd_next(marketing) if cmd == "next" else cmd_status(marketing)
    if len(argv) != 3:
        print(f"usage: {argv[0]} {cmd} FILE")
        return 2
    path = (ROOT / argv[2]).resolve()
    if not path.is_file():
        print(f"no such file: {argv[2]}")
        return 2
    return cmd_check(path) if cmd == "check" else cmd_record(path)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
