// Renders tools/share-preview/index.html to public/social-thumbnail.png at the
// standard 1200x630 Open Graph / Twitter summary_large_image size (1.91:1).
//
// The card is captured at 2x and downsampled back to 1200x630 so text and the
// dot grid stay crisp without shipping an oversized asset.
//
// Usage: node tools/share-preview/capture.mjs

import { writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const WIDTH = 1200
const HEIGHT = 630
const SCALE = 2

const source = fileURLToPath(new URL('./index.html', import.meta.url))
const output = fileURLToPath(
  new URL('../../public/social-thumbnail.png', import.meta.url)
)

const browser = await chromium.launch()

const page = await browser.newPage({
  viewport: { width: WIDTH, height: HEIGHT },
  deviceScaleFactor: SCALE
})

await page.goto(`file://${source}`, { waitUntil: 'networkidle' })
await page.evaluate(() => document.fonts.ready)

const oversized = await page.screenshot({
  clip: { x: 0, y: 0, width: WIDTH, height: HEIGHT }
})

const resizer = await browser.newPage()
const dataUrl = await resizer.evaluate(
  async ([base64, width, height]) => {
    const bitmap = await createImageBitmap(
      await (await fetch(`data:image/png;base64,${base64}`)).blob()
    )
    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height
    const context = canvas.getContext('2d')
    context.imageSmoothingEnabled = true
    context.imageSmoothingQuality = 'high'
    context.drawImage(bitmap, 0, 0, width, height)
    return canvas.toDataURL('image/png')
  },
  [oversized.toString('base64'), WIDTH, HEIGHT]
)

await writeFile(output, Buffer.from(dataUrl.split(',')[1], 'base64'))
await browser.close()

console.log(`Wrote ${output} (${WIDTH}x${HEIGHT})`)
