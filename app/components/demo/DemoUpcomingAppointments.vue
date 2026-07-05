<script setup lang="ts">
/**
 * Carousel slide 1: faithful replica of the app dashboard's "Upcoming
 * appointments" cards, fanned like paperwork over the demo canvas.
 *
 * Markup and classes mirror the app's appointment-list.vue card. At this
 * width (~300px, below the app's `sm` breakpoint) the real card renders its
 * stacked arrangement — identity cluster above, type badges below — so the
 * replica uses that arrangement unconditionally.
 */
type AppointmentTypeColor = 'error' | 'success' | 'warning' | 'info'

interface DemoAppointment {
  id: string
  petName: string
  time: string
  checkedIn: boolean
  imageUrl?: string
  sex: 'male' | 'female'
  species: 'dog' | 'cat'
  breed: string
  appointmentType: string
  procedure?: string
  /** Fanned placement within the canvas; later cards sit on top. */
  positionClass: string
}

// Mirrors the app's appointmentTypeColor(): Emergency → error,
// New Patient → success, Procedure → warning, everything else → info.
const typeColors: Record<string, AppointmentTypeColor> = {
  Emergency: 'error',
  'New Patient': 'success',
  Procedure: 'warning'
}

const appointmentTypeColor = (type: string): AppointmentTypeColor =>
  typeColors[type] ?? 'info'

const appointments: DemoAppointment[] = [
  {
    id: 'appt-001',
    petName: 'Waffles',
    time: '9:30 AM',
    checkedIn: false,
    imageUrl: '/demo/pets/waffles.jpg',
    sex: 'male',
    species: 'dog',
    breed: 'Corgi',
    appointmentType: 'Routine Checkup',
    positionClass: 'left-0 top-[10%] z-10 sm:left-1 sm:top-[19%]'
  },
  {
    id: 'appt-002',
    petName: 'Miso',
    time: '10:15 AM',
    checkedIn: true,
    imageUrl: '/demo/pets/miso.jpg',
    sex: 'female',
    species: 'cat',
    breed: 'Siamese',
    appointmentType: 'New Patient',
    positionClass: 'left-[6%] top-[30%] z-20 sm:left-[18%] sm:top-[42%]'
  },
  {
    id: 'appt-003',
    petName: 'Luna',
    time: '11:30 AM',
    checkedIn: false,
    sex: 'female',
    species: 'dog',
    breed: 'Beagle',
    appointmentType: 'Procedure',
    procedure: 'dental',
    positionClass: 'right-0 bottom-0 z-30 sm:right-1 sm:bottom-1'
  }
]

// macOS-active-window style layered shadow in light mode; the same layers
// recolored into a brand-green glow in dark mode (where a dark shadow would
// be invisible).
const cardShadow =
  'shadow-[0_0_0_0.5px_rgba(0,0,0,0.05),0_10px_28px_rgba(0,0,0,0.18),0_2px_8px_rgba(0,0,0,0.10)] dark:shadow-[0_0_0_1px_color-mix(in_oklab,var(--ui-primary)_18%,transparent),0_10px_28px_color-mix(in_oklab,var(--ui-primary)_12%,transparent),0_2px_8px_color-mix(in_oklab,var(--ui-primary)_8%,transparent)]'
</script>

<template>
  <DemoCanvas>
    <div class="hidden sm:block absolute left-[7%] top-[11%] text-sm font-semibold text-muted">
      Today
    </div>

    <button
      v-for="appt in appointments"
      :key="appt.id"
      type="button"
      class="absolute w-[min(300px,88%)] block rounded-lg text-left cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/60"
      :class="appt.positionClass"
    >
      <UCard
        class="bg-default ring-inset hover:bg-[color-mix(in_oklab,var(--ui-bg-elevated)_60%,var(--ui-bg))] hover:border-primary/60 transition-colors"
        :class="cardShadow"
        :ui="{ body: 'p-3 sm:p-4' }"
      >
        <div class="flex flex-col gap-3">
          <div class="flex items-start gap-3 flex-1 min-w-0">
            <UAvatar
              :src="appt.imageUrl"
              :alt="appt.petName"
              size="lg"
              icon="i-lucide-paw-print"
              class="border border-muted"
            />

            <div class="flex flex-col gap-2 min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <span class="font-semibold text-lg leading-tight truncate">{{ appt.petName }}</span>
                <UBadge color="neutral" variant="soft">
                  {{ appt.time }}
                </UBadge>
                <UBadge v-if="appt.checkedIn" color="success" variant="soft" class="capitalize">
                  checked in
                </UBadge>
              </div>

              <div class="flex flex-wrap items-center gap-2">
                <UBadge
                  color="info"
                  variant="soft"
                  :icon="appt.sex === 'male' ? 'i-lucide-mars' : 'i-lucide-venus'"
                  class="rounded-full capitalize"
                  :class="appt.sex === 'male' ? 'bg-blue-400/40 text-blue-500 dark:text-blue-300' : 'bg-pink-400/40 text-pink-500 dark:text-pink-300'"
                >
                  {{ appt.sex }}
                </UBadge>

                <UBadge
                  color="info"
                  variant="soft"
                  :icon="appt.species === 'dog' ? 'i-lucide-dog' : 'i-lucide-cat'"
                  class="rounded-full capitalize"
                >
                  {{ appt.species }}
                </UBadge>

                <UBadge color="info" variant="soft" class="rounded-full capitalize">
                  {{ appt.breed }}
                </UBadge>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <UBadge :color="appointmentTypeColor(appt.appointmentType)" variant="soft" class="capitalize">
              <strong>{{ appt.appointmentType }}</strong>
            </UBadge>
            <UBadge
              v-if="appt.procedure"
              :color="appointmentTypeColor('Procedure')"
              variant="soft"
              class="capitalize"
            >
              {{ appt.procedure }}
            </UBadge>
          </div>
        </div>
      </UCard>
    </button>
  </DemoCanvas>
</template>
