<script setup lang="ts">
const route = useRoute();

const items = computed(() => [
	{
		label: "Home",
		to: "/",
	},
	{
		label: "Features",
		to: "/features",
	},
	{
		label: "Pricing",
		to: "/pricing",
	},
	{
		label: "Docs",
		to: "/docs",
		active: route.path.startsWith("/docs"),
	},
]);
</script>

<template>
  <UHeader>
    <template #left>
      <NuxtLink to="/" class="flex items-center gap-2">
        <AppLogo class="w-9 h-9" />
        <p class="text-xl text-primary font-extrabold">Lucy<span class="text-default font-normal">VPMS</span></p>
      </NuxtLink>
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
        variant="outline"
        to="https://app.lucy.vet"
        block
      />
    </template>
  </UHeader>
</template>
