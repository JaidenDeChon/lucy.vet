<script setup lang="ts">
/**
 * Shared stage for live UI demos: a neutral, thin-bordered backdrop card
 * with a fixed aspect ratio so every demo occupies the same footprint.
 *
 * Content in the `card` slot is clipped to the backdrop card (for demos that
 * are intentionally cut off at the edges). Content in the default slot lives
 * in the outer coordinate space so it can protrude past the card edges.
 */
withDefaults(
  defineProps<{
    /** Extra classes for the backdrop card element. */
    cardClass?: string
  }>(),
  { cardClass: '' }
)
</script>

<template>
  <div class="demo-app-ui relative w-full aspect-[16/11] sm:aspect-[16/10] select-none">
    <div
      class="absolute inset-x-3 inset-y-5 sm:inset-x-6 sm:inset-y-7 rounded-xl border border-default bg-elevated/40 overflow-hidden"
      :class="cardClass"
    >
      <slot name="card" />
    </div>
    <slot />
  </div>
</template>
