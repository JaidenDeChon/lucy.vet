---
name: humanize-copy
description: Run the copy-humanizer agent on a loop, one file at a time, so every sentence and label on the lucy.vet marketing site is checked against the humanizer skill and rewritten to sound human, and to make sense to a clinic owner, practice manager or vet seeing Lucy VPMS for the first time, without losing or adding a claim. Use when asked to humanize the site, clean up AI-sounding or salesy copy, UI text, feature cards, pricing copy or SEO descriptions, or run the humanizer loop. Optional args are a file path to do just that one, a number N to stop after N files, or `marketing` to skip the template docs and auth pages.
---

# Humanize copy on a loop

Drives `.claude/agents/copy-humanizer.md` one file at a time. The agent takes the next item from `python3 scripts/humanize_copy.py next`, goes through it sentence by sentence with `.claude/skills/humanizer/SKILL.md`, verifies with `scripts/humanize_copy.py check`, `bun run lint` and `bun run typecheck` (plus `bun run build` for a content file), records the item in `.claude/humanized-copy.json`, and commits locally. This skill repeats that and pushes the results.

The default queue walks the Vue files that carry copy on the marketing pages and the site chrome first (`AppHeader.vue`, `AppFooter.vue`, `AppLogo.vue`, `pages/index.vue`, the showcase and calendar preview, `pages/pricing.vue`, `app.vue`, `error.vue`), so every button and nav item has its final name before the content that refers to it is rewritten. Then come `content/0.index.yml`, `content/1.features.yml` and `content/2.pricing.yml`, then the auth pages, any page or component added since the list was written, and last the template docs in `content/1.docs/`. After every item is done once, an item whose content changed since it was humanized comes back into the queue.

The marketing sweep (`marketing`) uses `python3 scripts/humanize_copy.py next --marketing`: the same queue without the auth pages and the docs.

## Arguments

- **A file path:** run the agent once on that file, then stop.
- **`marketing`** (optionally followed by N): work the marketing sweep instead of the default queue.
- **A number N:** stop after N files.
- **No arguments:** keep going until the agent reports `ALL DONE`, or something blocks.

## Before the first iteration

Make sure `node_modules` exists (`bun install --frozen-lockfile` if not). Run `python3 scripts/humanize_copy.py status` (with `--marketing` in that sweep) and tell the user how many items are done and how many remain.

## Each iteration

1. Dispatch the `copy-humanizer` agent in the foreground, one at a time. Pass the file if one was given; otherwise give no target (and in the marketing sweep, tell it to work the marketing sweep). Never let parallel runs pick their own "next" item: they would take the same one and collide on the ledger.
   - Docs pages (`content/1.docs/**/*.md`) may run in parallel batches if each agent is given an explicit, distinct path and told not to record or commit, because nothing else refers to their wording. After the batch, for each page: run `check`, spot-check it (step 3), then `record` and commit it yourself, one commit per page. Vue files and the three marketing content files always run one at a time, because later items depend on the names they settle on and `content/0.index.yml` shares text with the share card and `app/pages/index.vue`.
2. Read its report:
   - **`ALL DONE`** → stop.
   - **A blocker** (uncommitted changes on the file, a check or build it could not pass without losing meaning) → tell the user what's blocking and stop. Don't retry blindly.
3. Spot-check the commit. `git show --stat HEAD` must touch only that file and the ledger. The allowed extras are a test that asserts the file's wording, and for `content/0.index.yml` the share card (`tools/share-preview/index.html`), plus, if the image was regenerated, the new PNG, `app/app.vue` and `tools/share-preview/capture.mjs`. Then skim `git show HEAD -- "<file>"` for a changed or dropped promise: a security or compliance word, a price, a limit, an offer ("2 months free"), release status ("Pre-Alpha"), a comparison made stronger or weaker, a feature that grew ("reduce no-shows" becoming "eliminate no-shows"), a new claim, or edited placeholder or testimonial text. If you find one, fix it in a follow-up commit before moving on.
4. Push every 5 items, and at the end: `git push -u origin <current branch>`. If there's no open PR for the branch, open one. Never push to the default branch.
5. Give the user a one-line status per item: path, copy changed, main patterns removed. For a UI file, list any renamed control, and pass that rename to every later agent in the sweep so content uses the new name. Carry forward, and repeat at the end, anything the agents flagged for a human: a stale share image, a label whose target disagrees with it, a missing aria label, an SEO description over 160 characters, placeholder text still waiting for real copy.

## Pacing

The queue is small (about two dozen items), so a single session can usually finish it. Each content file needs a build of about two minutes. For an unattended run, prefer `/loop /humanize-copy 5` or a scheduled Routine that invokes this skill with a number, so each firing does a batch in a fresh context.
