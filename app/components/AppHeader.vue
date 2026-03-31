<script setup lang="ts">
const route = useRoute();

const items = computed(() => [
	{
		label: "Features",
		to: "/features",
	},
	{
		label: "Pricing",
		to: "/pricing",
	},
	{
		label: "Blog",
		to: "/blog",
	},
	{
		label: "Docs",
		to: "/docs",
		active: route.path.startsWith("/docs"),
	},
	{
		label: "Changelog",
		to: "/changelog",
	},
]);
</script>

<template>
  <UHeader>
    <template #left>
      <NuxtLink to="/">
        <AppLogo class="w-auto h-6 shrink-0" />
      </NuxtLink>
      <TemplateMenu />
    </template>

    <UNavigationMenu
      :items="items"
      variant="link"
    />

    <template #right>
      <UColorModeButton />

      <UButton
        icon="i-lucide-log-in"
        color="neutral"
        variant="ghost"
        to="/login"
        class="lg:hidden"
      />

      <UButton
        label="Sign in"
        color="neutral"
        variant="outline"
        to="https://app.lucy.vet"
        class="hidden lg:inline-flex"
      />
    </template>

    <template #body>
      <UNavigationMenu
        :items="items"
        orientation="vertical"
        class="-mx-2.5"
      />

      <USeparator class="my-6" />

      <UButton
        label="Sign in"
        color="neutral"
        variant="subtle"
        to="/login"
        block
        class="mb-3"
      />
      <UButton
        label="Sign up"
        color="neutral"
        to="/signup"
        block
      />
    </template>
  </UHeader>
</template>
