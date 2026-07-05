<script setup lang="ts">
/**
 * Rotating showcase of live UI demos for the "Built for veterinary clinics"
 * section. Autoplay pauses while the visitor's mouse is over the showcase so
 * they can interact with each demo, and resumes when they leave.
 */
const slides = [
  { key: 'appointments', label: 'Upcoming appointments' },
  { key: 'patients', label: 'Patients and parents' },
  { key: 'billing', label: 'Billing ledger' },
  { key: 'inventory', label: 'Inventory' }
] as const
</script>

<template>
  <UCarousel
    v-slot="{ item }"
    :items="[...slides]"
    loop
    dots
    :autoplay="{ delay: 8000, stopOnMouseEnter: true, stopOnInteraction: false }"
    :ui="{ item: 'basis-full' }"
    :aria-label="'Live previews of the Lucy VPMS interface'"
  >
    <DemoUpcomingAppointments v-if="item.key === 'appointments'" />
    <DemoPatientsTable v-else-if="item.key === 'patients'" />
    <DemoBillingLedger v-else-if="item.key === 'billing'" />
    <DemoInventoryTable v-else />
  </UCarousel>
</template>
