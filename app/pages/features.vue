<script setup lang="ts">
const { data: page } = await useAsyncData('features', () =>
  queryCollection('features').first()
)

const title = page.value?.seo?.title || page.value?.title
const description = page.value?.seo?.description || page.value?.description

useSeoMeta({
  title,
  ogTitle: title,
  description,
  ogDescription: description
})
</script>

<template>
  <div v-if="page">
    <UPageHero
      :title="page.title"
      :description="page.description"
    />

    <UPageSection
      v-for="(section, index) in page.sections"
      :id="section.id"
      :key="section.id || index"
      :title="section.title"
      :description="section.description"
      :orientation="section.orientation"
      :reverse="section.reverse"
      :features="section.features"
    >
      <LazyDemoCalendarPreview v-if="section.demo === 'calendar'" />
      <NuxtImg
        v-else-if="section.image"
        :src="section.image.src"
        :alt="section.image.alt"
        width="1920"
        height="1005"
        class="w-full rounded-lg ring ring-default shadow-2xl"
      />
      <ImagePlaceholder v-else />
    </UPageSection>
  </div>
</template>
