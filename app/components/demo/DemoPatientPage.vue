<script setup lang="ts">
/**
 * Live facsimile of the app's /patient/[clientId] "Patients & Parents" page.
 * Desktop mode mirrors the real two-pane dashboard arrangement (pet card
 * column + Account Details panel); mobile mode mirrors the real stacked
 * arrangement of the same content. All data is hardcoded demo data. Pet
 * selection, tab switching and the Add Pet dialog work; everything else is
 * intentionally inert.
 *
 * NOTE: this component is rendered inside scaled-down frames, so it must not
 * use responsive (sm:/lg:) classes — layout differences branch on `mobile`.
 * The Add Pet dialog is recreated as an absolutely-positioned overlay inside
 * this component's root (a teleported UModal would escape the mini frame).
 */

interface DemoPet {
  id: string
  name: string
  species: 'dog' | 'cat'
  breed: string
  color: string
  sex: 'male' | 'female'
  reproductiveStatus: 'neutered' | 'spayed' | 'intact' | 'unknown'
  age: number
  weightKg: number
  dobInput: string
  dobLabel: string
  hasAppointmentToday: boolean
  imageUrl: string
}

interface DemoTab {
  label: string
  value: string
  icon?: string
}

interface DemoConsent {
  key: string
  label: string
  checked: boolean
  stateLabel: string
  metadata: string | null
}

interface DemoAppointment {
  id: string
  dateLabel: string
  typeLabel: string
  durationLabel: string
  timing: 'today' | 'upcoming' | null
  pastDue: boolean
  petNames: string[]
  statusLabel: string
}

interface DemoCommunication {
  id: string
  channelLabel: string
  icon: string
  summary: string
  dateLabel: string
  loggedBy: string
}

interface DemoPaymentMethod {
  id: string
  maskedNumber: string
  cardholder: string
  expiry: string
  expired: boolean
}

interface DemoLedgerEvent {
  id: string
  typeLabel: string
  title: string
  dateLabel: string
  pastDue: boolean
  deltaLabel: string
  runningLabel: string
}

withDefaults(defineProps<{ mobile?: boolean }>(), { mobile: false })

const client = {
  name: 'Maria Santos',
  email: 'maria.santos@example.com',
  phone: '(555) 201-8834',
  addressLineOne: '412 Birchwood Ln',
  city: 'Ann Arbor',
  stateProvince: 'MI',
  zipCode: '48103',
  notes: 'Prefers morning appointments.'
}

const pets: DemoPet[] = [
  {
    id: 'biscuit',
    name: 'Biscuit',
    species: 'dog',
    breed: 'Golden Retriever',
    color: 'Golden',
    sex: 'male',
    reproductiveStatus: 'neutered',
    age: 4,
    weightKg: 29.5,
    dobInput: '2022-03-14',
    dobLabel: '3/14/2022',
    hasAppointmentToday: true,
    imageUrl: '/demo/pets/biscuit.jpg'
  },
  {
    id: 'clementine',
    name: 'Clementine',
    species: 'cat',
    breed: 'Domestic Shorthair',
    color: 'Brown tabby',
    sex: 'female',
    reproductiveStatus: 'spayed',
    age: 3,
    weightKg: 3.8,
    dobInput: '2023-05-02',
    dobLabel: '5/2/2023',
    hasAppointmentToday: false,
    imageUrl: '/demo/pets/mochi.jpg'
  },
  {
    id: 'waffles',
    name: 'Waffles',
    species: 'dog',
    breed: 'Pembroke Welsh Corgi',
    color: 'Red and white',
    sex: 'male',
    reproductiveStatus: 'unknown',
    age: 2,
    weightKg: 12.8,
    dobInput: '2024-01-20',
    dobLabel: '1/20/2024',
    hasAppointmentToday: false,
    imageUrl: '/demo/pets/waffles.jpg'
  }
]

const clientTabs: DemoTab[] = [
  { label: 'General', icon: 'i-lucide-user-round', value: 'general' },
  { label: 'Billing', icon: 'i-lucide-receipt-text', value: 'billing' },
  {
    label: 'Communications',
    icon: 'i-lucide-message-square',
    value: 'communications'
  },
  {
    label: 'Appointments',
    icon: 'i-lucide-calendar-check',
    value: 'appointments'
  }
]

const petTabs: DemoTab[] = [
  { label: 'General', value: 'general' },
  { label: 'Medical', value: 'medical' },
  { label: 'History', value: 'history' }
]

const consents: DemoConsent[] = [
  {
    key: 'sms',
    label: 'SMS communications consent',
    checked: true,
    stateLabel: 'GRANTED',
    metadata: 'Last updated: Mar 4, 2026 · Source: Client portal'
  },
  {
    key: 'email',
    label: 'Email communications consent',
    checked: false,
    stateLabel: 'NOT SET',
    metadata: null
  }
]

const appointments: DemoAppointment[] = [
  {
    id: 'a1',
    dateLabel: 'Jul 5, 2026, 9:30 AM',
    typeLabel: 'Wellness Exam — Dental Cleaning',
    durationLabel: '30 min',
    timing: 'today',
    pastDue: false,
    petNames: ['Biscuit'],
    statusLabel: 'checked in'
  },
  {
    id: 'a2',
    dateLabel: 'Jul 22, 2026, 2:15 PM',
    typeLabel: 'Vaccination — Rabies Booster',
    durationLabel: '20 min',
    timing: 'upcoming',
    pastDue: false,
    petNames: ['Clementine'],
    statusLabel: 'scheduled'
  },
  {
    id: 'a3',
    dateLabel: 'May 18, 2026, 2:00 PM',
    typeLabel: 'Sick Visit',
    durationLabel: '45 min',
    timing: null,
    pastDue: true,
    petNames: ['Clementine'],
    statusLabel: 'completed'
  }
]

const communications: DemoCommunication[] = [
  {
    id: 'c1',
    channelLabel: 'Phone',
    icon: 'i-lucide-phone',
    summary: 'Called to confirm Thursday dental cleaning; owner confirmed.',
    dateLabel: 'Jun 30, 2026, 11:12 AM',
    loggedBy: 'Dr. Patel'
  },
  {
    id: 'c2',
    channelLabel: 'Email',
    icon: 'i-lucide-mail',
    summary:
      'Sent post-op care instructions for Clementine’s dental extraction.',
    dateLabel: 'Jun 12, 2026, 4:48 PM',
    loggedBy: 'Alex Rivera'
  },
  {
    id: 'c3',
    channelLabel: 'Internal note',
    icon: 'i-lucide-notebook-pen',
    summary:
      'Owner mentioned Biscuit scratching left ear; monitor at next visit.',
    dateLabel: 'May 28, 2026, 3:05 PM',
    loggedBy: 'Dr. Patel'
  }
]

const ledgerEvents: DemoLedgerEvent[] = [
  {
    id: 'l1',
    typeLabel: 'Invoice Issued',
    title: 'Sick Visit — Clementine',
    dateLabel: 'May 18, 2026, 3:05 PM',
    pastDue: true,
    deltaLabel: '+$42.00',
    runningLabel: 'Running $42.00'
  },
  {
    id: 'l2',
    typeLabel: 'Payment Recorded',
    title: 'Visa •••• 4242',
    dateLabel: 'Apr 2, 2026, 10:12 AM',
    pastDue: false,
    deltaLabel: '-$85.00',
    runningLabel: 'Running $0.00'
  },
  {
    id: 'l3',
    typeLabel: 'Invoice Issued',
    title: 'Wellness Exam — Biscuit',
    dateLabel: 'Apr 2, 2026, 9:58 AM',
    pastDue: false,
    deltaLabel: '+$85.00',
    runningLabel: 'Running $85.00'
  }
]

const paymentMethods: DemoPaymentMethod[] = [
  {
    id: 'pm1',
    maskedNumber: '•••• •••• •••• 4242',
    cardholder: 'Maria Santos',
    expiry: '04/27',
    expired: false
  },
  {
    id: 'pm2',
    maskedNumber: '•••• •••• •••• 8810',
    cardholder: 'Maria Santos',
    expiry: '11/25',
    expired: true
  }
]

const selectedPetId = ref<string | null>(null)
const selectedPet = computed(
  () => pets.find((pet) => pet.id === selectedPetId.value) ?? null
)
const clientTab = ref('general')
const isAddPetOpen = ref(false)

function selectPet(petId: string) {
  selectedPetId.value = petId
}

function clearSelectedPet() {
  selectedPetId.value = null
}
</script>

<template>
  <div class="relative isolate flex h-full w-full flex-col overflow-hidden bg-default text-default">
    <!-- Top app navbar -->
    <div
      class="flex h-16 shrink-0 items-center gap-1.5 border-b border-default bg-default"
      :class="mobile ? 'px-4' : 'px-6'"
    >
      <UButton
        icon="i-lucide-panel-left-close"
        color="neutral"
        variant="ghost"
        square
        aria-label="Toggle sidebar"
        class="cursor-pointer"
      />
      <h2 class="min-w-0 flex-1 truncate text-lg font-semibold capitalize text-highlighted">patient</h2>
      <UButton
        color="neutral"
        variant="ghost"
        square
        aria-label="Notifications (3 unread)"
        class="relative cursor-pointer"
      >
        <UIcon name="i-lucide-bell" class="size-5" />
        <span
          class="absolute -right-0.5 -top-0.5 h-4 min-w-4 rounded-full bg-info px-1 text-center text-[10px] font-medium leading-4 text-inverted"
        >
          3
        </span>
      </UButton>
    </div>

    <div class="flex min-h-0 flex-1" :class="mobile ? 'flex-col overflow-y-auto' : ''">
      <!-- Main column: breadcrumbs + pet cards -->
      <div class="flex flex-col" :class="mobile ? 'shrink-0' : 'min-w-0 flex-1 overflow-y-auto'">
        <div class="flex w-full border-b border-b-default p-6" :class="mobile ? 'flex-col' : 'flex-row'">
          <nav aria-label="Breadcrumb" class="mr-auto flex h-10 items-center text-sm">
            <button type="button" class="cursor-pointer font-medium text-muted transition-colors hover:text-default">
              Home
            </button>
            <span class="mx-2 text-muted">/</span>
            <button type="button" class="cursor-pointer font-medium text-muted transition-colors hover:text-default">
              Patients &amp; Parents
            </button>
            <span class="mx-2 text-muted">/</span>
            <span class="font-semibold text-primary">{{ client.name }}</span>
          </nav>

          <div class="relative z-10 ml-auto flex gap-2" :class="mobile ? 'mt-3' : ''">
            <UButton
              color="success"
              variant="soft"
              label="Add New Pet"
              icon="i-lucide-paw-print"
              class="cursor-pointer"
              @click="isAddPetOpen = true"
            />
            <UButton
              v-if="mobile"
              color="info"
              variant="soft"
              label="Parent Details"
              icon="i-lucide-user"
              class="cursor-pointer"
              @click="clearSelectedPet"
            />
          </div>
        </div>

        <div class="flex flex-col gap-3" :class="mobile ? 'px-4 py-4' : 'px-6 py-6'">
          <button
            v-for="pet in pets"
            :key="pet.id"
            type="button"
            class="patient-card w-full cursor-pointer rounded-lg border bg-elevated/40 p-4 text-sm transition-colors"
            :class="[
              mobile ? '' : 'px-6',
              pet.id === selectedPetId
                ? 'border-primary bg-primary/10 text-highlighted'
                : 'border-default text-toned hover:bg-primary/5'
            ]"
            @click="selectPet(pet.id)"
          >
            <div class="flex items-center gap-4">
              <UAvatar :src="pet.imageUrl" :alt="pet.name" size="lg" icon="i-lucide-paw-print" />
              <div class="flex flex-col items-start">
                <div class="text-md flex flex-wrap items-center gap-1">
                  <span :class="pet.id === selectedPetId ? 'font-bold' : 'font-medium'">{{ pet.name }}</span>
                  <span v-if="pet.hasAppointmentToday" class="font-medium text-primary">
                    - Appointment today
                  </span>
                </div>
                <div class="text-sm text-muted">{{ pet.age }} years old &middot; {{ pet.weightKg }} kg</div>
              </div>
            </div>

            <div class="mt-3 flex flex-wrap gap-2">
              <UBadge
                color="info"
                variant="soft"
                :icon="pet.sex === 'male' ? 'i-lucide-mars' : 'i-lucide-venus'"
                :class="`rounded-full capitalize ${pet.sex === 'male' ? 'bg-blue-400/40 text-blue-500 dark:text-blue-300' : 'bg-pink-400/40 text-pink-500 dark:text-pink-300'}`"
              >
                {{ pet.sex }}
              </UBadge>
              <UBadge
                :icon="pet.species === 'dog' ? 'i-lucide-dog' : 'i-lucide-cat'"
                color="info"
                variant="soft"
                class="rounded-full capitalize"
              >
                {{ pet.species }}
              </UBadge>
              <UBadge color="info" variant="soft" class="rounded-full capitalize">
                {{ pet.breed }}
              </UBadge>
              <UBadge
                v-if="pet.reproductiveStatus !== 'unknown'"
                color="neutral"
                variant="soft"
                icon="i-lucide-scissors"
                class="rounded-full capitalize"
              >
                {{ pet.reproductiveStatus }}
              </UBadge>
            </div>
          </button>
        </div>
      </div>

      <!-- Account Details panel (right pane on desktop, stacked below on mobile) -->
      <div
        class="flex flex-col bg-elevated/50"
        :class="mobile ? 'shrink-0 border-t border-default' : 'w-[400px] shrink-0 overflow-hidden border-l border-default'"
      >
        <div class="flex h-16 shrink-0 items-center gap-1.5 border-b border-default bg-default px-4">
          <UButton
            v-if="selectedPet"
            icon="i-lucide-x"
            color="neutral"
            variant="ghost"
            aria-label="Close details"
            class="cursor-pointer"
            @click="clearSelectedPet"
          />
          <div class="min-w-0 flex-1 truncate text-lg font-bold text-highlighted">
            {{ selectedPet?.name ?? 'Account Details' }}
          </div>
          <UButton
            icon="i-lucide-ellipsis"
            color="neutral"
            variant="ghost"
            square
            aria-label="More actions"
            class="cursor-pointer"
          />
        </div>

        <div :class="mobile ? '' : 'min-h-0 flex-1 overflow-y-auto'">
          <!-- Pet view -->
          <div v-if="selectedPet" class="form-template">
            <div class="flex flex-col gap-6 p-6">
              <UAvatar
                :src="selectedPet.imageUrl"
                :alt="selectedPet.name"
                size="3xl"
                class="mx-auto h-32 w-32 rounded-full object-cover text-3xl"
              />
              <div class="flex flex-col items-center justify-center">
                <h1 class="text-2xl font-bold">{{ selectedPet.name }}</h1>
                <p class="capitalize text-muted">{{ selectedPet.species }} - {{ selectedPet.breed }}</p>
                <p class="text-muted">DOB: {{ selectedPet.dobLabel }}</p>
              </div>
            </div>

            <form @submit.prevent>
              <UTabs
                :items="petTabs"
                variant="link"
                :content="false"
                size="xl"
                class="w-full"
                :ui="{ trigger: 'cursor-pointer' }"
              />

              <div class="space-y-6 p-6">
                <UFormField label="Name">
                  <UInput :model-value="selectedPet.name" size="xl" class="w-full" />
                </UFormField>

                <div class="flex gap-4">
                  <UFormField label="Species" class="w-full">
                    <button
                      type="button"
                      class="flex w-full cursor-pointer items-center justify-between gap-1.5 rounded-md bg-default px-3 py-2 text-base capitalize text-highlighted ring ring-inset ring-accented"
                    >
                      {{ selectedPet.species }}
                      <UIcon name="i-lucide-chevron-down" class="size-5 shrink-0 text-dimmed" />
                    </button>
                  </UFormField>

                  <UFormField label="Sex" class="w-full">
                    <button
                      type="button"
                      class="flex w-full cursor-pointer items-center justify-between gap-1.5 rounded-md bg-default px-3 py-2 text-base capitalize text-highlighted ring ring-inset ring-accented"
                    >
                      {{ selectedPet.sex }}
                      <UIcon name="i-lucide-chevron-down" class="size-5 shrink-0 text-dimmed" />
                    </button>
                  </UFormField>
                </div>

                <UFormField label="Reproductive Status">
                  <button
                    type="button"
                    class="flex w-full cursor-pointer items-center justify-between gap-1.5 rounded-md bg-default px-3 py-2 text-base capitalize text-highlighted ring ring-inset ring-accented"
                  >
                    {{ selectedPet.reproductiveStatus }}
                    <UIcon name="i-lucide-chevron-down" class="size-5 shrink-0 text-dimmed" />
                  </button>
                </UFormField>

                <div class="flex gap-4">
                  <UFormField label="Breed" class="w-full">
                    <UInput
                      :model-value="selectedPet.breed"
                      size="xl"
                      class="w-full"
                      placeholder="e.g. Labrador Retriever"
                    />
                  </UFormField>

                  <UFormField label="Color" class="w-full">
                    <UInput
                      :model-value="selectedPet.color"
                      size="xl"
                      class="w-full"
                      placeholder="e.g. Black and tan"
                    />
                  </UFormField>
                </div>

                <div class="flex gap-4">
                  <UFormField label="Date of Birth" class="w-full">
                    <UInput :model-value="selectedPet.dobInput" type="date" size="xl" class="w-full" />
                  </UFormField>

                  <UFormField label="Weight (kg)" class="w-full">
                    <UInput
                      :model-value="selectedPet.weightKg"
                      type="number"
                      step="0.1"
                      min="0"
                      size="xl"
                      class="w-full"
                    />
                  </UFormField>
                </div>
              </div>

              <div class="flex justify-end p-6 pt-0">
                <UButton color="primary" label="Save Changes" class="cursor-pointer" />
              </div>
            </form>
          </div>

          <!-- Client view -->
          <div v-else class="pt-4">
            <div class="form-template">
              <div class="flex flex-col gap-6 p-6">
                <UAvatar
                  :alt="client.name"
                  size="3xl"
                  class="mx-auto h-32 w-32 rounded-full object-cover text-3xl"
                />
                <div class="flex flex-col items-center justify-center">
                  <h1 class="text-2xl font-bold">{{ client.name }}</h1>
                  <p class="text-muted">{{ client.email }}</p>
                  <p class="text-muted">{{ client.phone }}</p>
                </div>
              </div>

              <form @submit.prevent>
                <UTabs
                  v-model="clientTab"
                  :items="clientTabs"
                  variant="link"
                  :content="false"
                  size="md"
                  class="w-full"
                  :ui="{ trigger: 'cursor-pointer', leadingIcon: 'size-3.5' }"
                />

                <!-- General tab -->
                <template v-if="clientTab === 'general'">
                  <div class="flex flex-col gap-4 p-6">
                    <div class="flex gap-4">
                      <UFormField label="First Name" class="w-full">
                        <UInput model-value="Maria" class="w-full" size="xl" />
                      </UFormField>
                      <UFormField label="Last Name" class="w-full">
                        <UInput model-value="Santos" class="w-full" size="xl" />
                      </UFormField>
                    </div>

                    <UFormField label="Email">
                      <UInput :model-value="client.email" type="email" class="w-full" size="xl" />
                    </UFormField>

                    <UFormField label="Phone">
                      <UInput :model-value="client.phone" type="tel" class="w-full" size="xl" />
                    </UFormField>

                    <div class="rounded-lg border border-default bg-elevated/30 p-4">
                      <div class="flex flex-col gap-1">
                        <h2 class="text-sm font-semibold text-highlighted">Communications consent</h2>
                        <p class="text-xs text-muted">
                          Pet parents can update these preferences through the client portal.
                        </p>
                      </div>

                      <div class="mt-4 flex flex-col gap-4">
                        <div
                          v-for="consent in consents"
                          :key="consent.key"
                          class="rounded-md border border-default bg-default/70 p-3"
                        >
                          <div class="flex items-start justify-between gap-3">
                            <UCheckbox :model-value="consent.checked" :label="consent.label" disabled />
                            <span class="text-xs font-medium uppercase tracking-wide text-muted">
                              {{ consent.stateLabel }}
                            </span>
                          </div>
                          <p v-if="consent.metadata" class="mt-2 text-xs text-muted">
                            {{ consent.metadata }}
                          </p>
                        </div>
                      </div>
                    </div>

                    <UFormField label="Address Line 1">
                      <UInput :model-value="client.addressLineOne" class="w-full" size="xl" />
                    </UFormField>

                    <UFormField label="Address Line 2">
                      <UInput class="w-full" size="xl" />
                    </UFormField>

                    <UFormField label="City">
                      <UInput :model-value="client.city" class="w-full" size="xl" />
                    </UFormField>

                    <UFormField label="State / Province">
                      <UInput :model-value="client.stateProvince" class="w-full" size="xl" />
                    </UFormField>

                    <UFormField label="Zip Code">
                      <UInput :model-value="client.zipCode" class="w-full" size="xl" />
                    </UFormField>

                    <UFormField label="Notes">
                      <UTextarea :model-value="client.notes" :rows="4" class="w-full" size="xl" />
                    </UFormField>
                  </div>

                  <div class="mt-6 flex justify-end space-x-4 border-t border-t-default p-6">
                    <UButton color="neutral" variant="ghost" class="cursor-pointer">Cancel</UButton>
                    <UButton color="primary" class="cursor-pointer">Save Changes</UButton>
                  </div>
                </template>

                <!-- Billing tab -->
                <template v-else-if="clientTab === 'billing'">
                  <div class="flex flex-col border-t border-t-default">
                    <section class="px-6 py-4">
                      <div class="mb-3 flex items-center justify-between gap-3">
                        <h3 class="text-xs font-semibold uppercase tracking-wide text-muted">Billing Ledger</h3>
                        <UButton
                          icon="i-lucide-plus"
                          label="Ledger Event"
                          trailing-icon="i-lucide-chevron-down"
                          color="primary"
                          variant="soft"
                          size="xs"
                          class="cursor-pointer"
                        />
                      </div>
                      <div class="mb-3 flex flex-wrap gap-2">
                        <UBadge
                          color="warning"
                          variant="soft"
                          icon="i-lucide-alert-triangle"
                          label="Past Due: $42.00"
                        />
                      </div>

                      <div class="mt-4 flex flex-col gap-4">
                        <UPageCard v-for="event in ledgerEvents" :key="event.id" variant="subtle">
                          <template #title>
                            <div class="flex flex-wrap items-center gap-2">
                              <UBadge variant="soft" color="neutral" :label="event.typeLabel" />
                              <UBadge
                                v-if="event.pastDue"
                                variant="soft"
                                color="warning"
                                icon="i-lucide-alert-triangle"
                                label="Past Due"
                              />
                              <span class="truncate text-sm font-semibold text-highlighted">
                                {{ event.title }}
                              </span>
                            </div>
                          </template>
                          <template #description>
                            <span class="text-xs text-muted">{{ event.dateLabel }}</span>
                          </template>

                          <div class="flex flex-wrap items-start justify-between gap-3">
                            <div class="ml-auto text-right">
                              <p class="text-sm font-semibold text-highlighted">{{ event.deltaLabel }}</p>
                              <p class="text-xs text-muted">{{ event.runningLabel }}</p>
                            </div>
                          </div>
                        </UPageCard>
                      </div>
                    </section>

                    <section class="border-t border-t-default px-6 py-4">
                      <div class="mb-3 flex items-center justify-between gap-3">
                        <h3 class="text-xs font-semibold uppercase tracking-wide text-muted">Payment Methods</h3>
                        <UButton
                          icon="i-lucide-plus"
                          label="Payment Method"
                          color="primary"
                          variant="soft"
                          size="xs"
                          class="cursor-pointer"
                        />
                      </div>
                      <div class="overflow-x-auto">
                        <table class="w-full text-xs">
                          <thead>
                            <tr class="text-muted">
                              <th class="w-8 py-1.5 pr-3 text-left"></th>
                              <th class="py-1.5 pr-3 text-left font-medium">Number</th>
                              <th class="py-1.5 pr-3 text-left font-medium">Cardholder</th>
                              <th class="py-1.5 text-left font-medium">Expires</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              v-for="method in paymentMethods"
                              :key="method.id"
                              class="border-b border-b-default transition-colors last:border-0 hover:bg-elevated/50"
                            >
                              <td class="py-2 pr-3">
                                <UIcon name="i-lucide-credit-card" class="text-base text-muted" />
                              </td>
                              <td class="whitespace-nowrap py-2 pr-3 font-mono tabular-nums">
                                {{ method.maskedNumber }}
                                <UBadge
                                  v-if="method.expired"
                                  label="Expired"
                                  color="error"
                                  variant="soft"
                                  size="xs"
                                  class="ml-1.5"
                                />
                              </td>
                              <td class="max-w-28 truncate py-2 pr-3 text-muted">{{ method.cardholder }}</td>
                              <td class="py-2 tabular-nums text-muted">{{ method.expiry }}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </section>

                    <section class="border-t border-t-default px-6 py-4">
                      <div class="mb-3 flex items-center justify-between gap-3">
                        <h3 class="text-xs font-semibold uppercase tracking-wide text-muted">À La Carte Charges</h3>
                        <UButton
                          icon="i-lucide-plus"
                          label="Charge"
                          color="primary"
                          variant="soft"
                          size="xs"
                          class="cursor-pointer"
                        />
                      </div>
                      <p class="py-2 text-sm text-muted">No à la carte charges on file.</p>
                    </section>
                  </div>
                </template>

                <!-- Communications tab -->
                <template v-else-if="clientTab === 'communications'">
                  <div class="flex flex-col gap-0">
                    <div class="flex items-center justify-between border-b border-b-default px-6 py-4">
                      <h3 class="text-md font-semibold">Communications</h3>
                      <UButton
                        icon="i-lucide-plus"
                        color="primary"
                        variant="soft"
                        size="sm"
                        label="Log Communication"
                        class="cursor-pointer"
                      />
                    </div>

                    <div class="divide-y divide-default">
                      <div v-for="entry in communications" :key="entry.id" class="flex gap-4 px-6 py-4">
                        <div class="mt-1 flex-shrink-0">
                          <UIcon :name="entry.icon" class="text-xl text-muted" />
                        </div>
                        <div class="flex min-w-0 flex-1 flex-col gap-1">
                          <div class="flex items-center justify-between gap-2">
                            <UBadge
                              :label="entry.channelLabel"
                              color="neutral"
                              variant="soft"
                              size="sm"
                              class="capitalize"
                            />
                            <span class="flex-shrink-0 whitespace-nowrap text-xs text-muted">
                              {{ entry.dateLabel }}
                            </span>
                          </div>
                          <p class="text-sm leading-snug text-default">{{ entry.summary }}</p>
                          <div class="mt-1 flex items-center justify-between">
                            <span class="text-xs text-muted">Logged by {{ entry.loggedBy }}</span>
                            <div class="flex gap-1">
                              <UButton
                                icon="i-lucide-pencil"
                                color="neutral"
                                variant="ghost"
                                size="xs"
                                aria-label="Edit entry"
                                class="cursor-pointer"
                              />
                              <UButton
                                icon="i-lucide-trash-2"
                                color="error"
                                variant="ghost"
                                size="xs"
                                aria-label="Delete entry"
                                class="cursor-pointer"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- Appointments tab -->
                <template v-else-if="clientTab === 'appointments'">
                  <div class="flex flex-col gap-0">
                    <div class="flex items-center justify-between border-b border-b-default px-6 py-4">
                      <h3 class="text-md font-semibold">Appointments</h3>
                    </div>

                    <div class="flex flex-col gap-3 px-6 py-4">
                      <button
                        v-for="appt in appointments"
                        :key="appt.id"
                        type="button"
                        class="w-full cursor-pointer rounded-lg border border-default p-4 text-left transition-colors hover:border-primary/40 hover:bg-primary/5"
                      >
                        <div class="mb-2 flex items-start justify-between gap-3">
                          <div>
                            <p class="text-sm font-semibold">{{ appt.dateLabel }}</p>
                            <p class="mt-0.5 text-xs text-muted">{{ appt.typeLabel }}</p>
                          </div>
                          <p class="flex-shrink-0 whitespace-nowrap text-xs text-muted">{{ appt.durationLabel }}</p>
                        </div>
                        <div class="flex flex-wrap gap-1.5">
                          <UBadge v-if="appt.timing === 'today'" label="Today" color="success" variant="soft" size="xs" />
                          <UBadge
                            v-else-if="appt.timing === 'upcoming'"
                            label="Upcoming"
                            color="success"
                            variant="soft"
                            size="xs"
                          />
                          <UBadge v-if="appt.pastDue" label="Past Due" color="error" variant="soft" size="xs" />
                          <UBadge
                            v-for="petName in appt.petNames"
                            :key="petName"
                            :label="petName"
                            color="neutral"
                            variant="soft"
                            size="xs"
                            leading-icon="i-lucide-paw-print"
                          />
                          <UBadge
                            :label="appt.statusLabel"
                            color="neutral"
                            variant="outline"
                            size="xs"
                            class="capitalize"
                          />
                        </div>
                      </button>
                    </div>
                  </div>
                </template>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Pet dialog: recreated in-frame (a teleported UModal would escape the mini frame) -->
    <div
      v-if="isAddPetOpen"
      class="absolute inset-0 z-30 flex items-center justify-center"
      :class="mobile ? 'p-3' : 'p-6'"
    >
      <button
        type="button"
        class="absolute inset-0 cursor-default bg-elevated/75 backdrop-blur-sm"
        aria-label="Close dialog"
        @click="isAddPetOpen = false"
      />

      <div
        role="dialog"
        aria-modal="true"
        aria-label="Add Pet"
        class="relative flex max-h-full w-full max-w-2xl flex-col divide-y divide-default overflow-hidden rounded-lg bg-default shadow-lg ring ring-default"
      >
        <div class="flex items-start gap-1.5" :class="mobile ? 'p-4' : 'px-6 py-4'">
          <div class="min-w-0 flex-1">
            <h2 class="font-semibold text-highlighted">Add Pet</h2>
            <p class="mt-1 text-sm text-muted">Create a new patient record under the current client.</p>
          </div>
          <UButton
            icon="i-lucide-x"
            color="neutral"
            variant="ghost"
            square
            aria-label="Close"
            class="cursor-pointer"
            @click="isAddPetOpen = false"
          />
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto" :class="mobile ? 'p-4' : 'p-6'">
          <div class="flex flex-col gap-4">
            <UFormField label="Pet Name" required>
              <UInput placeholder="Pet's name" disabled class="w-full" />
            </UFormField>

            <div class="grid grid-cols-2 gap-4">
              <UFormField label="Species" required>
                <button
                  type="button"
                  disabled
                  class="flex w-full cursor-not-allowed items-center justify-between gap-1.5 rounded-md bg-default px-2.5 py-1.5 text-sm text-dimmed opacity-75 ring ring-inset ring-accented"
                >
                  Select species
                  <UIcon name="i-lucide-chevron-down" class="size-5 shrink-0 text-dimmed" />
                </button>
              </UFormField>

              <UFormField label="Sex" required>
                <button
                  type="button"
                  disabled
                  class="flex w-full cursor-not-allowed items-center justify-between gap-1.5 rounded-md bg-default px-2.5 py-1.5 text-sm text-dimmed opacity-75 ring ring-inset ring-accented"
                >
                  Select sex
                  <UIcon name="i-lucide-chevron-down" class="size-5 shrink-0 text-dimmed" />
                </button>
              </UFormField>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <UFormField label="Breed">
                <UInput placeholder="e.g. Labrador Retriever" disabled class="w-full" />
              </UFormField>

              <UFormField label="Color" required>
                <UInput placeholder="e.g. Black, Tan" disabled class="w-full" />
              </UFormField>
            </div>

            <UFormField label="Reproductive Status">
              <button
                type="button"
                disabled
                class="flex w-full cursor-not-allowed items-center justify-between gap-1.5 rounded-md bg-default px-2.5 py-1.5 text-sm text-highlighted opacity-75 ring ring-inset ring-accented"
              >
                Unknown
                <UIcon name="i-lucide-chevron-down" class="size-5 shrink-0 text-dimmed" />
              </button>
            </UFormField>

            <div class="grid grid-cols-2 gap-4">
              <UFormField label="Date of Birth" required>
                <UInput type="date" disabled class="w-full" />
              </UFormField>

              <UFormField label="Weight (kg)" required>
                <UInput type="number" placeholder="e.g. 4.5" step="0.001" min="0" disabled class="w-full" />
              </UFormField>
            </div>

            <UFormField label="Notes">
              <UTextarea placeholder="Optional patient notes (one per line)" :rows="3" disabled class="w-full" />
            </UFormField>
          </div>
        </div>

        <div :class="mobile ? 'p-4' : 'px-6 py-4'">
          <div class="flex w-full justify-end gap-2">
            <UButton color="neutral" variant="ghost" label="Cancel" disabled class="disabled:cursor-not-allowed" />
            <UButton
              color="primary"
              label="Add Pet"
              icon="i-lucide-paw-print"
              disabled
              class="disabled:cursor-not-allowed"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
