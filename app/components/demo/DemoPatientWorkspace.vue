<script setup lang="ts">
/**
 * Homepage "Designed for zero friction" composition: two overlapping live
 * frames of the patient page — a desktop window scaled down from a 1024px
 * design width and a phone frame scaled down from 390px, tucked over the
 * window's bottom-right corner. Each frame is authored at a fixed design
 * size and shrunk with a CSS transform so every hover state, tab, pet
 * selection and dialog stays fully interactive at miniature size. The
 * wrapper's height is set to the scaled height so surrounding layout
 * reserves the right space at any viewport width, and the phone always
 * stays inside the component box (no horizontal overflow).
 */

const DESKTOP_WIDTH = 1024
const DESKTOP_HEIGHT = 680
const PHONE_WIDTH = 390
const PHONE_HEIGHT = 780

const container = ref<HTMLElement | null>(null)
const { width: containerWidth } = useElementSize(container)

const layout = computed(() => {
  // Fallback matches a typical marketing demo column before first measure;
  // the max-w-2xl wrapper caps how large the composition can grow.
  const width = containerWidth.value || 560
  // The desktop window leaves a right gutter for the phone to poke past it.
  const desktopWidth = Math.round(width * 0.88)
  const desktopScale = desktopWidth / DESKTOP_WIDTH
  const desktopHeight = Math.round(DESKTOP_HEIGHT * desktopScale)
  // Phone height tracks the window height, clamped so it stays legible on
  // narrow viewports and never dwarfs the window on wide ones.
  const phoneHeight = Math.round(
    Math.min(Math.max(desktopHeight * 0.72, 170), 420)
  )
  const phoneScale = phoneHeight / PHONE_HEIGHT
  const phoneWidth = Math.round(PHONE_WIDTH * phoneScale)
  // How far the phone drops below the window's bottom edge.
  const phoneDrop = Math.round(phoneHeight * 0.14)
  return {
    desktopScale,
    desktopWidth,
    desktopHeight,
    phoneScale,
    phoneWidth,
    phoneHeight,
    totalHeight: desktopHeight + phoneDrop
  }
})
</script>

<template>
  <div
    ref="container"
    class="demo-app-ui relative mx-auto w-full max-w-2xl"
    :style="{ height: `${layout.totalHeight}px` }"
  >
    <!-- Desktop window frame -->
    <div
      class="demo-window-shadow absolute left-0 top-0 overflow-hidden rounded-xl bg-default ring ring-default"
      :style="{ width: `${layout.desktopWidth}px`, height: `${layout.desktopHeight}px` }"
    >
      <div
        :style="{
          width: `${DESKTOP_WIDTH}px`,
          height: `${DESKTOP_HEIGHT}px`,
          transform: `scale(${layout.desktopScale})`,
          transformOrigin: 'top left'
        }"
      >
        <DemoPatientPage />
      </div>
    </div>

    <!-- Phone frame overlapping the window's bottom-right corner -->
    <div
      class="demo-phone-shadow absolute bottom-0 right-0 z-10 overflow-hidden rounded-2xl bg-default ring ring-default"
      :style="{ width: `${layout.phoneWidth}px`, height: `${layout.phoneHeight}px` }"
    >
      <div
        :style="{
          width: `${PHONE_WIDTH}px`,
          height: `${PHONE_HEIGHT}px`,
          transform: `scale(${layout.phoneScale})`,
          transformOrigin: 'top left'
        }"
      >
        <DemoPatientPage mobile />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* macOS-active-window style layered shadow */
.demo-window-shadow {
  box-shadow:
    0 0 0 0.5px rgb(0 0 0 / 0.06),
    0 2px 6px rgb(0 0 0 / 0.08),
    0 12px 24px rgb(0 0 0 / 0.12),
    0 28px 64px rgb(0 0 0 / 0.2);
}

.demo-phone-shadow {
  box-shadow:
    0 2px 6px rgb(0 0 0 / 0.12),
    0 12px 32px rgb(0 0 0 / 0.28);
}
</style>
