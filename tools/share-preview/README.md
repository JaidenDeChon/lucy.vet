# Share preview

`public/social-thumbnail-v2.png` is the Open Graph / Twitter card image
referenced from `app/app.vue` (`ogImage` + `twitterImage`).

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

## Why the filename is versioned

Social platforms cache OG images by URL, often for a long time and with no way
to force a refresh short of their own debug tools. Overwriting the bytes at a
path that has already been scraped means most places keep showing the old card.

So when the card changes meaningfully, **give it a new filename** (bump the
suffix) and update the two references in `app/app.vue` and the `output` path in
`capture.mjs`. That is what makes a redesigned card actually show up.

## A note on deploy previews

Absolute URLs are resolved against the site URL, which `nuxt.config.ts` points
at `DEPLOY_PRIME_URL` on Netlify deploy previews and branch deploys. Without
that, a preview's `og:image` would point at production `lucy.vet` and a share
card for a PR would show whatever is already live rather than the branch being
reviewed.
