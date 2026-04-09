<script setup lang="ts">
const { data: page } = await useAsyncData('index', () =>
  queryCollection('index').first()
)

const isVerticalLayout = useMediaQuery('(max-width: 1023px)')
type IndexPageContentExtras = {
  hero?: { badge?: { label?: string } }
  demo?: { title?: string }
}

const heroBadgeLabel = computed(() =>
  (
    (page.value as unknown as IndexPageContentExtras | null)?.hero?.badge
      ?.label ?? ''
  ).trim()
)
const demoSectionTitle = computed(() =>
  (
    (page.value as unknown as IndexPageContentExtras | null)?.demo?.title ??
    'Watch the demo'
  ).trim()
)

const title = page.value?.seo?.title || page.value?.title
const description = page.value?.seo?.description || page.value?.description

useSeoMeta({
  titleTemplate: '',
  title,
  ogTitle: title,
  description,
  ogDescription: description
})
</script>

<template>
  <div v-if="page">
    <UPageHero
      :links="page.hero.links"
      orientation="horizontal"
      :ui="{ headline: '-mt-34' }"
    >
      <template #top>
        <HeroBackground />
      </template>

      <template #title>
        <Motion
          :initial="{
            scale: 1.1,
            opacity: 0,
            filter: 'blur(20px)'
          }"
          :animate="{
            scale: 1,
            opacity: 1,
            filter: 'blur(0px)'
          }"
          :transition="{
            duration: 0.6,
            delay: isVerticalLayout ? 0.3 : 0.2
          }"
        >
          <MDC
            :value="page.title"
            unwrap="p"
          />
        </Motion>
      </template>

      <template #description>
        <Motion
          :initial="{
            scale: 1.1,
            opacity: 0,
            filter: 'blur(20px)'
          }"
          :animate="{
            scale: 1,
            opacity: 1,
            filter: 'blur(0px)'
          }"
          :transition="{
            duration: 0.6,
            delay: isVerticalLayout ? 0.3 : 0.2
          }"
        >
          <p>{{ page.description }}</p>
        </Motion>
      </template>

      <template #headline>
        <Motion
          :initial="{
            scale: 1.1,
            opacity: 0,
            filter: 'blur(20px)'
          }"
          :animate="{
            scale: 1,
            opacity: 1,
            filter: 'blur(0px)'
          }"
          :transition="{
            duration: 0.6,
            delay: isVerticalLayout ? 0.2 : 0.1
          }"
        >
          <UBadge
            color="primary"
            variant="subtle"
            size="md"
          >
            {{ heroBadgeLabel }}
          </UBadge>
        </Motion>
      </template>

      <template #links>
        <Motion
          v-for="(link, index) in page.hero.links"
          :key="index"
          :initial="{
            scale: 1.1,
            opacity: 0,
            filter: 'blur(20px)'
          }"
          :animate="{
            scale: 1,
            opacity: 1,
            filter: 'blur(0px)'
          }"
          :transition="{
            duration: 0.6,
            delay: 0.4
          }"
        >
          <UButton
            v-bind="link"
          />
        </Motion>
      </template>

      <Motion
        class="order-first lg:order-last mt-"
        :initial="{
          scale: 1.1,
          opacity: 0,
          filter: 'blur(20px)'
        }"
        :animate="{
          scale: 1,
          opacity: 1,
          filter: 'blur(0px)'
        }"
        :transition="{
          duration: 0.6,
          delay: isVerticalLayout ? 0.1 : 0.4
        }"
      >
        <NuxtPicture
          src="lucy.png"
          format="webp"
          width="1495"
          height="1576"
          :img-attrs="{ class: '-mt-12 mx-auto max-w-xs w-full lg:max-w-lg lg:-mt-16' }"
        />
      </Motion>
    </UPageHero>

    <UPageSection
      id="watch-the-demo"
      :title="demoSectionTitle"
    >
      <ImagePlaceholder />
    </UPageSection>

    <UPageSection
      v-for="(section, index) in page.sections"
      :key="index"
      :title="section.title"
      :description="section.description"
      :orientation="section.orientation"
      :reverse="section.reverse"
      :features="section.features"
    >
      <ImagePlaceholder />
    </UPageSection>

    <UPageSection
      :title="page.features.title"
      :description="page.features.description"
    >
      <UPageGrid>
        <UPageCard
          v-for="(item, index) in page.features.items"
          :key="index"
          v-bind="item"
          spotlight
        />
      </UPageGrid>
    </UPageSection>

    <UPageSection
      id="testimonials"
      :headline="page.testimonials.headline"
      :title="page.testimonials.title"
      :description="page.testimonials.description"
    >
      <UPageColumns class="xl:columns-4">
        <UPageCard
          v-for="(testimonial, index) in page.testimonials.items"
          :key="index"
          variant="subtle"
          :description="testimonial.quote"
          :ui="{ description: 'before:content-[open-quote] after:content-[close-quote]' }"
        >
          <template #footer>
            <UUser
              v-bind="testimonial.user"
              size="lg"
            />
          </template>
        </UPageCard>
      </UPageColumns>
    </UPageSection>

    <USeparator />

    <UPageCTA
      v-bind="page.cta"
      variant="naked"
      class="overflow-hidden"
    >
      <LazyStarsBg />
    </UPageCTA>
  </div>
</template>
