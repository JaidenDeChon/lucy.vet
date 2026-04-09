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
      <ImagePlaceholder />
    </UPageSection>
  </div>
</template>
