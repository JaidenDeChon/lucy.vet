# Share preview

`public/social-thumbnail.png` is the Open Graph / Twitter card image referenced
from `app/app.vue` (`ogImage` + `twitterImage`).

It is generated from `index.html`, a hand-built HTML recreation of the home page
hero — same dark background, primary glow and dot grid as
`app/components/HeroBackground.vue`, the same badge, headline and copy as
`content/0.index.yml`, and the real `public/lucy.png` photo.

## Regenerating

```sh
node tools/share-preview/capture.mjs
```

This needs `playwright` available to Node (`bun install` at the repo root does
not pull it in — install it globally or with `npx playwright@1.56 ...`).

The script renders the card at 2x and downsamples it to **1200x630** — the
standard 1.91:1 size for `summary_large_image` cards, which is what Facebook,
LinkedIn, Slack, Discord and X all expect.

## Editing

Change the copy or layout in `index.html`, re-run the capture script, and commit
the regenerated PNG. `index.html` loads Public Sans from Google Fonts (the same
face the site uses), so the machine running the capture needs network access.
