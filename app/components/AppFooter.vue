<script setup lang="ts">
const columns = [
	{
		label: "Resources",
		children: [
			{
				label: "Docs",
			},
		],
	},
	{
		label: "Features",
		children: [
			{
				label: "Calendar",
			},
			{
				label: "Record keeping",
			},
			{
				label: "Inventory",
			},
			{
				label: "Customer portal",
			},
		],
	},
	{
		label: "Company",
		children: [
			{
				label: "About",
			},
			{
				label: "Pricing",
				to: "/pricing",
			},
		],
	},
];

const toast = useToast();

const email = ref("");
const loading = ref(false);

function onSubmit() {
	loading.value = true;

	toast.add({
		title: "Subscribed!",
		description: "You've been subscribed to our newsletter.",
	});
}
</script>

<template>
  <USeparator class="h-px">
    <NuxtPicture src="app-logo.svg" :width="140" />
  </USeparator>

  <UFooter :ui="{ top: 'border-b border-default mt-8' }">
    <template #top>
      <UContainer>
        <UFooterColumns :columns="columns">
          <template #right>
            <form @submit.prevent="onSubmit">
              <UFormField
                name="email"
                label="Subscribe to our newsletter"
                size="lg"
              >
                <UInput
                  v-model="email"
                  type="email"
                  class="w-full"
                  placeholder="Enter your email"
                >
                  <template #trailing>
                    <UButton
                      type="submit"
                      size="xs"
                      color="neutral"
                      label="Subscribe"
                    />
                  </template>
                </UInput>
              </UFormField>
            </form>
          </template>
        </UFooterColumns>
      </UContainer>
    </template>

    <template #left>
      <p class="text-muted text-sm">
        Jaiden DeChon • © {{ new Date().getFullYear() }}
      </p>
    </template>
  </UFooter>
</template>
