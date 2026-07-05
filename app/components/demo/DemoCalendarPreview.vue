<script setup lang="ts">
/**
 * "Keeps you on schedule" demo: real-markup replica of the product's
 * calendar month grid (weekday header + day cells + appointment chips),
 * deliberately cropped at the demo card edges. Day cells and chips reuse
 * the exact classes from the product's calendar-grid.vue and
 * calendar-event-chip.vue; the type→color map mirrors
 * appointmentTypeChipClass(). All appointments are fictional and every
 * control is inert.
 */

type DemoAppointmentType =
  | 'Routine Checkup'
  | 'New Patient'
  | 'Follow-up'
  | 'Consultation'
  | 'Procedure'
  | 'Emergency'

interface DemoAppointment {
  /** Preformatted start time, e.g. "9:00 AM". */
  time: string
  /**
   * Chip title and color driver. The real product's chips deliberately show
   * only the appointment type (never pet or owner names); mirror that here.
   */
  type: DemoAppointmentType
}

interface DemoDay {
  key: string
  day: number
  inMonth: boolean
  isToday: boolean
  appointments: DemoAppointment[]
}

/** Mirrors MAX_VISIBLE_EVENTS in the product's calendar-grid.vue. */
const maxVisibleAppointments = 3

/** Mirrors DAY_OF_WEEK_LABELS (Sunday-first) from the product. */
const weekdayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

/** Mirrors appointmentTypeChipClass() from the product exactly. */
const chipClassByType: Record<DemoAppointmentType, string> = {
  Emergency: 'bg-error/15 text-error-700 dark:text-error-300',
  'New Patient': 'bg-success/15 text-success-700 dark:text-success-300',
  Procedure: 'bg-warning/20 text-warning-800 dark:text-warning-200',
  'Follow-up': 'bg-info/15 text-info-700 dark:text-info-300',
  'Routine Checkup': 'bg-info/15 text-info-700 dark:text-info-300',
  Consultation: 'bg-info/15 text-info-700 dark:text-info-300'
}

function makeDay(
  day: number,
  inMonth: boolean,
  appointments: DemoAppointment[] = [],
  isToday = false
): DemoDay {
  return {
    key: `${inMonth ? 'jul' : 'jun'}-${day}`,
    day,
    inMonth,
    isToday,
    appointments
  }
}

// Four week rows (June 28 – July 25). The bottom rows crop at the card edge;
// row four is crop insurance and never fully renders.
const demoDays: DemoDay[] = [
  makeDay(28, false),
  makeDay(29, false),
  makeDay(30, false),
  makeDay(1, true, [
    { time: '9:00 AM', type: 'Routine Checkup' },
    { time: '10:30 AM', type: 'New Patient' },
    { time: '1:15 PM', type: 'Procedure' },
    { time: '2:45 PM', type: 'Follow-up' },
    { time: '4:00 PM', type: 'Routine Checkup' }
  ]),
  makeDay(2, true, [{ time: '11:00 AM', type: 'Consultation' }]),
  makeDay(3, true, [{ time: '8:30 AM', type: 'Procedure' }]),
  makeDay(4, true),
  makeDay(
    5,
    true,
    [
      { time: '9:15 AM', type: 'Routine Checkup' },
      { time: '2:00 PM', type: 'Follow-up' }
    ],
    true
  ),
  makeDay(6, true, [{ time: '7:45 AM', type: 'Emergency' }]),
  makeDay(7, true, [{ time: '10:00 AM', type: 'Routine Checkup' }]),
  makeDay(8, true, [{ time: '9:30 AM', type: 'New Patient' }]),
  makeDay(9, true, [{ time: '1:00 PM', type: 'Follow-up' }]),
  makeDay(10, true, [{ time: '11:15 AM', type: 'Procedure' }]),
  makeDay(11, true),
  makeDay(12, true),
  makeDay(13, true),
  makeDay(14, true, [{ time: '10:45 AM', type: 'Routine Checkup' }]),
  makeDay(15, true),
  makeDay(16, true),
  makeDay(17, true),
  makeDay(18, true),
  ...Array.from({ length: 7 }, (_, index) => makeDay(19 + index, true))
]
</script>

<template>
  <DemoCanvas>
    <template #card>
      <p class="sr-only">
        Preview of the Lucy calendar month view with sample appointments.
      </p>

      <!-- Fixed grid width: the trailing weekday columns crop at the card's
           right edge and the third week row crops at the bottom, on purpose.
           gap-4 between header row and grid mirrors the product's
           `calendar-grid flex flex-col gap-4` wrapper. -->
      <div class="calendar-grid min-w-[40rem] flex flex-col gap-4" aria-hidden="true">
        <!-- Day-of-week header row -->
        <div class="grid grid-cols-7 border-b border-default">
          <div
            v-for="label in weekdayLabels"
            :key="label"
            class="py-2 text-center text-xs font-semibold text-muted uppercase tracking-wide"
          >
            {{ label }}
          </div>
        </div>

        <!-- Day grid: container gives the top line, cells give bottom/right
             (single-pixel lines); the card's own border supplies the left. -->
        <div class="grid grid-cols-7 auto-rows-fr border-t border-default">
          <div
            v-for="cell in demoDays"
            :key="cell.key"
            :class="[
              'calendar-day-cell cursor-pointer border-b border-r border-default p-1 min-h-[96px] flex flex-col gap-1 overflow-hidden transition-colors',
              cell.inMonth ? 'bg-background' : 'bg-muted/30',
              cell.isToday
                ? 'bg-primary/5 ring-1 ring-inset ring-primary/60'
                : 'hover:bg-primary/5'
            ]"
          >
            <!-- Day number: today = solid primary circle; the cell also keeps
                 the selected ring/tint because the product pre-selects today -->
            <div class="flex items-center justify-end">
              <span
                :class="[
                  'text-xs font-medium w-6 h-6 flex items-center justify-center rounded-full',
                  cell.isToday
                    ? 'bg-primary text-white dark:text-white'
                    : cell.inMonth
                      ? 'text-default'
                      : 'text-muted'
                ]"
              >
                {{ cell.day }}
              </span>
            </div>

            <!-- Appointment chips -->
            <div class="flex flex-col gap-0.5 overflow-hidden">
              <button
                v-for="appointment in cell.appointments.slice(0, maxVisibleAppointments)"
                :key="`${cell.key}-${appointment.time}`"
                type="button"
                tabindex="-1"
                :title="`${appointment.time} ${appointment.type}`"
                :class="[
                  'calendar-event-chip flex items-center gap-1 rounded px-1.5 py-0.5 text-xs leading-tight cursor-pointer truncate focus:outline-none focus-visible:ring-1 focus-visible:ring-primary/60',
                  chipClassByType[appointment.type]
                ]"
              >
                <span class="shrink-0 opacity-80">{{ appointment.time }}</span>
                <span class="truncate font-semibold underline decoration-current/40 underline-offset-2">
                  {{ appointment.type }}
                </span>
              </button>

              <!-- Overflow indicator -->
              <div
                v-if="cell.appointments.length > maxVisibleAppointments"
                class="text-xs text-muted pl-1 leading-tight"
              >
                +{{ cell.appointments.length - maxVisibleAppointments }} more
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </DemoCanvas>
</template>
