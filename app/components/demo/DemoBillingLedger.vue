<script setup lang="ts">
/**
 * Live replica of the Lucy app's /clinic/billing/ledger content column:
 * grouped ledger events with nested child rows showing open, past-due and
 * settled billing states. The column slowly auto-scrolls to showcase the
 * full anatomy; hovering pauses it and any manual scroll inside hands
 * control back to the visitor for the rest of the page visit.
 */

interface LedgerRow {
  id: string
  badge: string
  timestamp: string
  label: string
  delta: string
  running: string
  /** Indentation step relative to the group root (1.25rem per level). */
  depth: number
  pastDue?: boolean
  reason?: string
}

interface LedgerGroupBase {
  id: string
  title: string
  clientId: string
  timestamp: string
  pastDue?: boolean
}

interface LedgerMultiGroup extends LedgerGroupBase {
  kind: 'multi'
  rows: LedgerRow[]
}

interface LedgerSingleGroup extends LedgerGroupBase {
  kind: 'single'
  badge: string
  delta: string
  running: string
  reason?: string
}

type LedgerGroup = LedgerMultiGroup | LedgerSingleGroup

const tabItems = [
  { label: 'Ledger', icon: 'i-lucide-book-open-text', active: true },
  { label: 'Invoices', icon: 'i-lucide-file-text' },
  { label: 'Payments', icon: 'i-lucide-credit-card' }
]

// Friendly event names matching the badges shown in the list below —
// digestible at a glance but still meaningful to clinic staff.
const eventTypeItems = [
  { label: 'All Events', value: 'all' },
  { label: 'Quote Created', value: 'quote-created' },
  { label: 'Invoice Issued', value: 'invoice-issued' },
  { label: 'Payment Received', value: 'payment-received' },
  { label: 'Refund Issued', value: 'refund-issued' },
  { label: 'Adjustment', value: 'adjustment' },
  { label: 'Credit', value: 'credit' }
]

const clientIdFilter = ref('')
const eventTypeFilter = ref('all')

const groups: LedgerGroup[] = [
  {
    kind: 'multi',
    id: 'wellness',
    title: 'Annual Wellness Exam',
    clientId: 'abcd1234',
    timestamp: 'Jun 18, 2026, 9:15 AM',
    rows: [
      {
        id: 'wellness-quote',
        badge: 'Quote Created',
        timestamp: 'Jun 18, 2026, 9:15 AM',
        label: 'Annual Wellness Exam',
        delta: '$0.00',
        running: '$0.00',
        depth: 0
      },
      {
        id: 'wellness-invoice',
        badge: 'Invoice Issued',
        timestamp: 'Jun 18, 2026, 11:40 AM',
        label: 'Annual Wellness Exam',
        delta: '+$65.00',
        running: '$65.00',
        depth: 1
      },
      {
        id: 'wellness-payment',
        badge: 'Payment Received',
        timestamp: 'Jun 19, 2026, 2:30 PM',
        label: 'Manual Payment',
        delta: '-$60.00',
        running: '$5.00',
        depth: 2
      },
      {
        id: 'wellness-adjustment',
        badge: 'Adjustment',
        timestamp: 'Jun 19, 2026, 4:45 PM',
        label: 'Courtesy adjustment',
        reason: 'Courtesy billing adjustment',
        delta: '-$5.00',
        running: '$0.00',
        depth: 2
      }
    ]
  },
  {
    kind: 'multi',
    id: 'dental',
    title: 'Dental Cleaning',
    clientId: 'efgh5678',
    timestamp: 'Jun 20, 2026, 11:00 AM',
    pastDue: true,
    rows: [
      {
        id: 'dental-invoice',
        badge: 'Invoice Issued',
        timestamp: 'Jun 20, 2026, 11:00 AM',
        label: 'Dental Cleaning',
        delta: '+$240.00',
        running: '$240.00',
        depth: 0,
        pastDue: true
      },
      {
        id: 'dental-payment',
        badge: 'Payment Received',
        timestamp: 'Jun 21, 2026, 3:20 PM',
        label: 'Card Payment',
        delta: '-$60.00',
        running: '$180.00',
        depth: 1
      }
    ]
  },
  {
    kind: 'multi',
    id: 'microchip',
    title: 'Microchip Procedure',
    clientId: 'ijkl9012',
    timestamp: 'Jun 24, 2026, 10:05 AM',
    rows: [
      {
        id: 'microchip-invoice',
        badge: 'Invoice Issued',
        timestamp: 'Jun 24, 2026, 10:05 AM',
        label: 'Microchip Procedure',
        delta: '+$45.00',
        running: '$225.00',
        depth: 0
      },
      {
        id: 'microchip-payment',
        badge: 'Payment Received',
        timestamp: 'Jun 25, 2026, 9:30 AM',
        label: 'Payment at Checkout',
        delta: '-$45.00',
        running: '$180.00',
        depth: 1
      }
    ]
  },
  {
    kind: 'single',
    id: 'account-payment',
    badge: 'Payment Received',
    title: 'Manual Payment',
    clientId: 'mnop3456',
    timestamp: 'Jun 27, 2026, 4:12 PM',
    delta: '-$120.00',
    running: '$60.00'
  },
  {
    kind: 'single',
    id: 'referral-credit',
    badge: 'Credit',
    title: 'Referral Credit',
    clientId: 'qrst7890',
    timestamp: 'Jul 2, 2026, 2:45 PM',
    reason: 'Referral thank-you credit',
    delta: '-$25.00',
    running: '$35.00'
  }
]

// --- Auto-scroll showcase -------------------------------------------------

const scroller = ref<HTMLElement | null>(null)
const motionPreference = usePreferredReducedMotion()

const SCROLL_SPEED = 15 // px per second
const BOTTOM_PAUSE = 1500 // ms to rest at the bottom
const TOP_PAUSE = 1200 // ms to rest back at the top
const RETURN_DURATION = 900 // ms for the eased return to top

type ScrollPhase = 'down' | 'bottomPause' | 'returning' | 'topPause'

let rafId = 0
let stopped = false
let hovering = false
let lastTick = 0
let lastWrite = 0
let waited = 0
let returnFrom = 0
let pos = 0
let phase: ScrollPhase = 'down'

function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2
}

function step(timestamp: number): void {
  if (stopped) return
  rafId = requestAnimationFrame(step)
  if (hovering) {
    lastTick = 0
    return
  }
  const el = scroller.value
  if (!el) return
  if (lastTick === 0) {
    lastTick = timestamp
    return
  }
  // Clamp dt so background-tab gaps don't cause a jump.
  const dt = Math.min(timestamp - lastTick, 100)
  lastTick = timestamp
  const max = el.scrollHeight - el.clientHeight
  if (max <= 0) return

  if (phase === 'down') {
    pos = Math.min(pos + (SCROLL_SPEED * dt) / 1000, max)
    if (pos >= max) {
      phase = 'bottomPause'
      waited = 0
    }
  } else if (phase === 'bottomPause') {
    waited += dt
    if (waited >= BOTTOM_PAUSE) {
      phase = 'returning'
      returnFrom = pos
      waited = 0
    }
  } else if (phase === 'returning') {
    waited += dt
    const progress = Math.min(waited / RETURN_DURATION, 1)
    pos = returnFrom * (1 - easeInOutCubic(progress))
    if (progress >= 1) {
      pos = 0
      phase = 'topPause'
      waited = 0
    }
  } else {
    waited += dt
    if (waited >= TOP_PAUSE) phase = 'down'
  }

  lastWrite = performance.now()
  el.scrollTop = pos
}

function stopAutoScroll(): void {
  stopped = true
  if (rafId) cancelAnimationFrame(rafId)
  rafId = 0
}

function onPointerEnter(): void {
  hovering = true
}

function onPointerLeave(): void {
  hovering = false
  lastTick = 0
  // Re-sync in case the browser nudged the scroll position while paused.
  if (!stopped && scroller.value) pos = scroller.value.scrollTop
}

/** Wheel or touch inside the column = the visitor takes over for good. */
function onUserScrollIntent(): void {
  stopAutoScroll()
}

function onScroll(): void {
  if (stopped || !hovering) return
  // Scroll while hovered can't come from us (we pause on hover); the time
  // guard only ignores the async event from our own final pre-hover write.
  if (performance.now() - lastWrite > 150) stopAutoScroll()
}

onMounted(() => {
  if (motionPreference.value === 'reduce') return
  rafId = requestAnimationFrame(step)
})

watch(motionPreference, (value) => {
  if (value === 'reduce') stopAutoScroll()
})

onBeforeUnmount(stopAutoScroll)
</script>

<template>
  <DemoCanvas @pointerenter="onPointerEnter" @pointerleave="onPointerLeave">
    <template #card>
      <div class="flex h-full w-full flex-col">
        <!-- Tabbed-column-page toolbar (Ledger tab active) -->
        <div
          class="flex min-h-[49px] shrink-0 items-center justify-between gap-1.5 overflow-x-auto border-b border-default px-4"
        >
          <div class="flex w-full flex-col gap-3 lg:flex-row lg:items-center">
            <UNavigationMenu highlight class="min-w-0 flex-1" :items="tabItems" />
          </div>
        </div>

        <!-- Scrollable ledger content column -->
        <div
          ref="scroller"
          class="min-h-0 flex-1 overflow-y-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          @wheel.passive="onUserScrollIntent"
          @touchmove.passive="onUserScrollIntent"
          @focusin="onUserScrollIntent"
          @scroll.passive="onScroll"
        >
          <div class="mx-auto flex w-full flex-col gap-4 p-4">
            <!-- Clinic balance chips -->
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-semibold uppercase tracking-wide text-muted">Clinic Balance</span>
              <UBadge color="primary" variant="soft">$35.00</UBadge>
            </div>

            <div class="flex flex-col gap-4">
              <!-- Filter bar -->
              <div
                class="grid grid-cols-[minmax(0,1fr)_130px_auto_auto] gap-3 rounded-lg border border-default bg-elevated/20 p-4"
              >
                <UFormField label="Client ID">
                  <UInput v-model="clientIdFilter" class="w-full" placeholder="abcd1234" />
                </UFormField>
                <UFormField label="Event Type">
                  <USelect v-model="eventTypeFilter" :items="eventTypeItems" class="w-full" />
                </UFormField>
                <div class="flex items-end">
                  <UButton label="Apply" color="primary" class="cursor-pointer" />
                </div>
                <div class="flex items-end">
                  <UButton label="Clear" color="neutral" variant="ghost" class="cursor-pointer" />
                </div>
              </div>

              <!-- Ledger list -->
              <div class="flex flex-col gap-4">
                <template v-for="group in groups" :key="group.id">
                  <!-- Multi-event group: nested child rows indented per depth -->
                  <UPageCard v-if="group.kind === 'multi'" variant="subtle">
                    <template #title>
                      <div class="flex flex-wrap items-center gap-2">
                        <UBadge
                          v-if="group.pastDue"
                          variant="soft"
                          color="warning"
                          icon="i-lucide-alert-triangle"
                        >
                          Past Due
                        </UBadge>
                        <span class="truncate text-sm font-semibold text-highlighted">{{ group.title }}</span>
                        <span class="text-xs text-muted">&middot; {{ group.clientId }}</span>
                      </div>
                    </template>
                    <template #description>
                      <span class="text-xs text-muted">{{ group.timestamp }}</span>
                    </template>

                    <div class="flex flex-col gap-2">
                      <article
                        v-for="row in group.rows"
                        :key="row.id"
                        class="rounded-md border p-3"
                        :class="row.pastDue ? 'border-warning bg-warning/5' : 'border-default bg-default/40'"
                        :style="{ marginLeft: `${row.depth * 1.25}rem` }"
                      >
                        <div class="flex flex-wrap items-start justify-between gap-3">
                          <div class="space-y-1">
                            <div class="flex flex-wrap items-center gap-2">
                              <UBadge variant="soft" color="neutral">{{ row.badge }}</UBadge>
                              <UBadge
                                v-if="row.pastDue"
                                variant="soft"
                                color="warning"
                                icon="i-lucide-alert-triangle"
                              >
                                Past Due
                              </UBadge>
                              <span class="text-xs text-muted">{{ row.timestamp }}</span>
                            </div>
                            <p class="text-sm font-medium text-highlighted">{{ row.label }}</p>
                            <p v-if="row.reason" class="text-xs text-muted">Reason: {{ row.reason }}</p>
                          </div>
                          <div class="text-right">
                            <p class="text-sm font-semibold text-highlighted">{{ row.delta }}</p>
                            <p class="text-xs text-muted">Running {{ row.running }}</p>
                          </div>
                        </div>
                      </article>
                    </div>
                  </UPageCard>

                  <!-- Single-event card -->
                  <UPageCard v-else variant="subtle">
                    <template #title>
                      <div class="flex flex-wrap items-center gap-2">
                        <UBadge variant="soft" color="neutral">{{ group.badge }}</UBadge>
                        <UBadge
                          v-if="group.pastDue"
                          variant="soft"
                          color="warning"
                          icon="i-lucide-alert-triangle"
                        >
                          Past Due
                        </UBadge>
                        <span class="truncate text-sm font-semibold text-highlighted">{{ group.title }}</span>
                        <span class="text-xs text-muted">&middot; {{ group.clientId }}</span>
                      </div>
                    </template>
                    <template #description>
                      <span class="text-xs text-muted">{{ group.timestamp }}</span>
                    </template>

                    <div class="flex flex-wrap items-start justify-between gap-3">
                      <p v-if="group.reason" class="text-xs text-muted">Reason: {{ group.reason }}</p>
                      <div class="ml-auto text-right">
                        <p class="text-sm font-semibold text-highlighted">{{ group.delta }}</p>
                        <p class="text-xs text-muted">Running {{ group.running }}</p>
                      </div>
                    </div>
                  </UPageCard>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </DemoCanvas>
</template>
