<script setup lang="ts">
/**
 * Rotating showcase of live UI demos for the "Built for veterinary clinics"
 * section. Autoplay pauses while the visitor's mouse is over the showcase so
 * they can interact with each demo, and resumes when they leave.
 *
 * The stock carousel dots are replaced with a custom pager: small round dots
 * (padded so the hitbox stays comfortable) where the active dot stretches
 * into a pill holding a progress fill for the current autoplay interval.
 * Clicking the active pill toggles the autoplay timer, and the fill freezes
 * or resumes to match.
 */
const slides = [
  { key: 'appointments', label: 'Upcoming appointments' },
  { key: 'patients', label: 'Patients and parents' },
  { key: 'billing', label: 'Billing ledger' },
  { key: 'inventory', label: 'Inventory' }
] as const

const AUTOPLAY_DELAY = 8000

// Stable references: the carousel re-inits embla whenever its autoplay prop
// changes identity, and this component re-renders every frame while the
// progress fill animates — inline literals here would reset the timer
// on every render.
const carouselItems = [...slides]
const autoplayOptions = {
  delay: AUTOPLAY_DELAY,
  stopOnMouseEnter: true,
  stopOnInteraction: false
}
const carouselUi = { item: 'basis-full' }

const carousel = useTemplateRef('carousel')

const selectedIndex = ref(0)
/** True once the visitor stops the timer by clicking the active pill. */
const isStopped = ref(false)
/** 0..1 fill of the active pill for the current autoplay interval. */
const progress = ref(0)

let rafId = 0
let teardown: (() => void) | null = null

// The fill tracks the plugin's own timer every frame: timeUntilNext()
// returns the remaining delay while the timer is armed and null while it is
// paused (hover) or stopped (pill click), so the fill freezes automatically.
function tick() {
  rafId = requestAnimationFrame(tick)
  const remaining = carousel.value?.emblaApi
    ?.plugins()
    ?.autoplay?.timeUntilNext()
  if (remaining != null) {
    progress.value = Math.min(1, Math.max(0, 1 - remaining / AUTOPLAY_DELAY))
  }
}

function wireEmbla(): boolean {
  const embla = carousel.value?.emblaApi
  if (!embla) return false
  const onSelect = () => {
    selectedIndex.value = embla.selectedScrollSnap()
    progress.value = 0
  }
  embla.on('select', onSelect)
  onSelect()
  teardown = () => {
    embla.off('select', onSelect)
  }
  return true
}

onMounted(() => {
  rafId = requestAnimationFrame(tick)
  // The carousel loads its embla plugins asynchronously; poll briefly until
  // the API is available.
  if (wireEmbla()) return
  const poll = setInterval(() => {
    if (wireEmbla()) clearInterval(poll)
  }, 100)
  setTimeout(() => clearInterval(poll), 5000)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  teardown?.()
})

function onDotClick(index: number) {
  const embla = carousel.value?.emblaApi
  if (!embla) return
  if (index !== selectedIndex.value) {
    embla.scrollTo(index)
    return
  }
  // Clicking the active pill toggles the autoplay timer.
  const autoplay = embla.plugins()?.autoplay
  if (!autoplay) return
  if (isStopped.value) {
    autoplay.play()
    isStopped.value = false
  } else {
    autoplay.stop()
    isStopped.value = true
  }
}
</script>

<template>
  <div>
    <UCarousel
      ref="carousel"
      v-slot="{ item }"
      :items="carouselItems"
      loop
      wheel-gestures
      :autoplay="autoplayOptions"
      :ui="carouselUi"
      aria-label="Live previews of the Lucy VPMS interface"
    >
      <DemoUpcomingAppointments v-if="item.key === 'appointments'" />
      <DemoPatientsTable v-else-if="item.key === 'patients'" />
      <DemoBillingLedger v-else-if="item.key === 'billing'" />
      <DemoInventoryTable v-else />
    </UCarousel>

    <div
      class="mt-3 flex items-center justify-center"
      role="tablist"
      aria-label="Showcase slides"
    >
      <button
        v-for="(slide, index) in slides"
        :key="slide.key"
        type="button"
        role="tab"
        class="group cursor-pointer p-2"
        :aria-selected="index === selectedIndex"
        :aria-label="
          index === selectedIndex
            ? `${slide.label} — click to ${isStopped ? 'resume' : 'stop'} auto-advance`
            : `Go to ${slide.label}`
        "
        @click="onDotClick(index)"
      >
        <!-- Active dot: elongated pill with an autoplay progress fill -->
        <span
          v-if="index === selectedIndex"
          class="relative block h-1.5 w-5 overflow-hidden rounded-full bg-accented"
        >
          <span
            class="absolute inset-y-0 left-0 rounded-full bg-primary transition-opacity duration-300"
            :class="isStopped ? 'opacity-40' : ''"
            :style="{ width: `${progress * 100}%` }"
          />
        </span>
        <!-- Inactive dots: small, with the padding keeping the hitbox large -->
        <span
          v-else
          class="block size-1.5 rounded-full bg-accented transition-colors group-hover:bg-primary/50"
        />
      </button>
    </div>
  </div>
</template>
