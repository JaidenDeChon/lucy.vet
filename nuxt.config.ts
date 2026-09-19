// https://nuxt.com/docs/api/configuration/nuxt-config

// Absolute URLs (canonical, og:image, twitter:image) are resolved against the
// site URL. On Netlify deploy previews and branch deploys, point them at that
// deploy's own origin - otherwise a preview advertises production's assets and
// share cards show whatever is live on lucy.vet rather than the branch under
// review. CONTEXT is 'production' only for the production deploy.
const isNetlifyPreview =
  !!process.env.CONTEXT && process.env.CONTEXT !== 'production'

const siteUrl =
  (isNetlifyPreview ? process.env.DEPLOY_PRIME_URL : undefined) ||
  process.env.NUXT_PUBLIC_SITE_URL ||
  process.env.URL ||
  undefined

export default defineNuxtConfig({
  modules: [
    '@nuxt/image',
    '@nuxt/ui',
    '@nuxt/content',
    '@vueuse/nuxt',
    'nuxt-og-image',
    'motion-v/nuxt'
  ],

  devtools: {
    enabled: true
  },

  site: {
    url: siteUrl
  },

  css: ['~/assets/css/main.css'],

  colorMode: {
    preference: 'system'
  },

  content: {
    experimental: {
      sqliteConnector: 'native'
    }
  },

  compatibilityDate: '2024-07-11',

  nitro: {
    prerender: {
      routes: ['/'],
      crawlLinks: true
    }
  },

  image: {}
})
