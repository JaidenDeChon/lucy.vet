<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'

/**
 * Live replica of the Lucy app's /patient/lookup clients table (Patients &
 * Parents). Markup, classes and interactions mirror the real page; the table
 * sits flush with the DemoCanvas card so rows crop deliberately at the
 * bottom edge. All data is hardcoded demo content and every action is inert.
 */

interface DemoPet {
  id: string
  name: string
  imageUrl: string
}

type AccountStanding = 'good' | 'past due' | 'delinquent' | 'suspended'

interface DemoClient {
  id: string
  firstName: string
  lastName: string
  email: string
  accountStanding: AccountStanding
  pets: DemoPet[]
}

const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')

const clients: DemoClient[] = [
  {
    id: 'c1',
    firstName: 'Ahmed',
    lastName: 'Khan',
    email: 'ahmed@cool.wow',
    accountStanding: 'good',
    pets: [{ id: 'p1', name: 'Biscuit', imageUrl: '/demo/pets/biscuit.jpg' }]
  },
  {
    id: 'c2',
    firstName: 'Harmen',
    lastName: 'Bos',
    email: 'harmen@cool.wow',
    accountStanding: 'past due',
    pets: [{ id: 'p2', name: 'Bruno', imageUrl: '/demo/pets/bruno.jpg' }]
  },
  {
    id: 'c3',
    firstName: 'Mikey',
    lastName: 'Cruz',
    email: 'mikey@cool.wow',
    accountStanding: 'good',
    pets: [
      { id: 'p3', name: 'Miso', imageUrl: '/demo/pets/miso.jpg' },
      { id: 'p4', name: 'Mochi', imageUrl: '/demo/pets/mochi.jpg' }
    ]
  },
  {
    id: 'c4',
    firstName: 'Tami',
    lastName: 'Wong',
    email: 'tami@cool.wow',
    accountStanding: 'delinquent',
    pets: [{ id: 'p5', name: 'Clover', imageUrl: '/demo/pets/clover.jpg' }]
  },
  {
    id: 'c5',
    firstName: 'Justin',
    lastName: 'Reed',
    email: 'justin@cool.wow',
    accountStanding: 'good',
    pets: [{ id: 'p6', name: 'Peanut', imageUrl: '/demo/pets/peanut.jpg' }]
  },
  {
    id: 'c6',
    firstName: 'Meghann',
    lastName: 'Hill',
    email: 'meghann@cool.wow',
    accountStanding: 'good',
    pets: [
      { id: 'p7', name: 'Pickles', imageUrl: '/demo/pets/pickles.jpg' },
      { id: 'p8', name: 'Smokey', imageUrl: '/demo/pets/smokey.jpg' }
    ]
  },
  {
    id: 'c7',
    firstName: 'Sam',
    lastName: 'Lee',
    email: 'sam@cool.wow',
    accountStanding: 'past due',
    pets: [{ id: 'p9', name: 'Olive', imageUrl: '/demo/pets/olive.jpg' }]
  },
  {
    id: 'c8',
    firstName: 'Tieme',
    lastName: 'Vos',
    email: 'tieme@cool.wow',
    accountStanding: 'good',
    pets: [{ id: 'p10', name: 'Waffles', imageUrl: '/demo/pets/waffles.jpg' }]
  },
  {
    id: 'c9',
    firstName: 'Joseph',
    lastName: 'Fox',
    email: 'joseph@cool.wow',
    accountStanding: 'good',
    pets: [{ id: 'p11', name: 'Ziggy', imageUrl: '/demo/pets/ziggy.jpg' }]
  }
]

const BADGE_COLOR: Record<AccountStanding, 'success' | 'warning' | 'error'> = {
  good: 'success',
  'past due': 'warning',
  delinquent: 'error',
  suspended: 'error'
}

// Local sorting state so the Client Name header menu works like the real app.
const sorting = ref<{ id: string; desc: boolean }[]>([])

const columns: TableColumn<DemoClient>[] = [
  {
    accessorKey: 'lastName',
    // Same render-function header as the real page: a ghost button that
    // opens an Asc/Desc dropdown and swaps its icon with the sort state.
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(
        UDropdownMenu,
        {
          content: { align: 'start' },
          'aria-label': 'Actions dropdown',
          items: [
            {
              label: 'Asc',
              type: 'checkbox',
              icon: 'i-lucide-arrow-up-narrow-wide',
              checked: isSorted === 'asc',
              onSelect: () => {
                if (isSorted === 'asc') {
                  column.clearSorting()
                } else {
                  column.toggleSorting(false)
                }
              }
            },
            {
              label: 'Desc',
              type: 'checkbox',
              icon: 'i-lucide-arrow-down-wide-narrow',
              checked: isSorted === 'desc',
              onSelect: () => {
                if (isSorted === 'desc') {
                  column.clearSorting()
                } else {
                  column.toggleSorting(true)
                }
              }
            }
          ]
        },
        () =>
          h(UButton, {
            color: 'neutral',
            variant: 'ghost',
            label: 'Client Name',
            icon: isSorted
              ? isSorted === 'asc'
                ? 'i-lucide-arrow-up-narrow-wide'
                : 'i-lucide-arrow-down-wide-narrow'
              : 'i-lucide-arrow-up-down',
            class: '-mx-2.5 data-[state=open]:bg-elevated'
          })
      )
    }
  },
  { accessorKey: 'accountStanding', header: 'Account Standing' },
  { accessorKey: 'pets', header: 'Pets' },
  { id: 'actions' }
]

// The real app's single menu item plus a few plausible actions; all inert.
const rowMenuItems = [
  { label: 'Open client account', icon: 'i-lucide-info' },
  { label: 'New appointment', icon: 'i-lucide-calendar-plus' },
  { label: 'New invoice', icon: 'i-lucide-receipt' },
  { label: 'Archive client', icon: 'i-lucide-archive' }
]

function onRowSelect() {
  // Rows navigate to the client profile in the real app; inert in the demo.
  // Binding @select keeps rows selectable so the real hover style applies.
}
</script>

<template>
  <DemoCanvas>
    <template #card>
      <!-- Flush to the card's top/left; the 1px offset hides the table's own
           border under the card border so the crop reads as a screenshot. -->
      <div class="absolute -inset-x-px -top-px">
        <UTable
          v-model:sorting="sorting"
          :data="clients"
          :columns="columns"
          sticky
          class="bg-elevated/20 rounded-md border border-default"
          :ui="{ thead: 'bg-elevated', tr: 'cursor-pointer' }"
          @select="onRowSelect"
        >
          <template #lastName-cell="{ row }">
            <div class="flex items-center gap-3">
              <UAvatar
                :alt="`${row.original.firstName} ${row.original.lastName}`"
                class="text-xs border border-muted"
              />
              <!-- Narrower than the real app so the pets column stays in view -->
              <div class="flex flex-col max-w-24">
                <span class="truncate">{{ row.original.lastName }}, {{ row.original.firstName }}</span>
                <span class="truncate text-xs text-muted">{{ row.original.email }}</span>
              </div>
            </div>
          </template>

          <template #accountStanding-cell="{ row }">
            <UBadge :color="BADGE_COLOR[row.original.accountStanding]" variant="soft" class="capitalize">
              {{ row.original.accountStanding }}
            </UBadge>
          </template>

          <template #pets-cell="{ row }">
            <UAvatarGroup>
              <UTooltip
                v-for="pet in row.original.pets"
                :key="pet.id"
                :text="pet.name"
                :content="{ side: 'top' }"
                arrow
              >
                <UAvatar :src="pet.imageUrl" :alt="pet.name" size="sm" />
              </UTooltip>
            </UAvatarGroup>
          </template>

          <template #actions-cell>
            <div class="text-right">
              <UDropdownMenu :items="rowMenuItems">
                <UButton
                  icon="i-lucide-ellipsis"
                  color="neutral"
                  variant="ghost"
                  class="cursor-pointer"
                  aria-label="Row actions"
                />
              </UDropdownMenu>
            </div>
          </template>
        </UTable>
      </div>
    </template>
  </DemoCanvas>
</template>
