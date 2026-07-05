<script setup lang="ts">
import type { DropdownMenuItem, TableColumn, TableRow } from '@nuxt/ui'

/**
 * Live replica of the Lucy app's /inventory supplies & medications table.
 * Markup, classes and interactions mirror the real page: red-chip item names,
 * category badges, warning/error row tints with hover intensification, and
 * the pointer-following state tooltip. The table sits flush with the
 * DemoCanvas card at real size, cropping deliberately at the right and
 * bottom edges. All data is hardcoded demo content and every action is inert.
 */

interface DemoInventoryCategory {
  key: string
  label: string
  color: string
}

interface DemoInventoryItem {
  id: number
  name: string
  category: DemoInventoryCategory
  quantity: number
  unit: string
  reorderLevel: number
  supplier: string
  lotNumber?: string
  expirationDate?: string
  costPerUnit: number
}

const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')

// Same raw Tailwind color pairs the real app stores on each category.
const CATEGORIES = {
  medical: {
    key: 'medical',
    label: 'Medical Supplies',
    color: 'bg-emerald-500 dark:bg-emerald-400'
  },
  medications: {
    key: 'medications',
    label: 'Medications',
    color: 'bg-purple-500 dark:bg-purple-400'
  },
  fluids: {
    key: 'fluids',
    label: 'Fluids & Medications',
    color: 'bg-sky-500 dark:bg-sky-400'
  }
} satisfies Record<string, DemoInventoryCategory>

const MS_PER_DAY = 864e5
const FOURTEEN_DAYS_MS = 14 * MS_PER_DAY
const EXPIRING_SOON_WINDOW_DAYS = 30

// Relative dates keep the expiring/expired rows flagged no matter when the
// demo is viewed — same approach as the real app's dummy data.
const expiringSoonDate = new Date(Date.now() + FOURTEEN_DAYS_MS).toString()
const expiredDate = new Date(Date.now() - FOURTEEN_DAYS_MS).toString()

// Ordered as a story: healthy stock, then running low, expiring soon,
// expired and out of stock, with more healthy rows below the crop.
const INVENTORY_ITEMS: DemoInventoryItem[] = [
  {
    id: 1,
    name: 'Exam Gloves (Nitrile)',
    category: CATEGORIES.medical,
    quantity: 240,
    unit: 'boxes',
    reorderLevel: 80,
    supplier: 'Cascade Vet Supply',
    lotNumber: 'EG-26-0412',
    expirationDate: '2028-03-01',
    costPerUnit: 6.25
  },
  // WARNING: quantity at/below the reorder point.
  {
    id: 2,
    name: 'Rabies Vaccine (1 yr)',
    category: CATEGORIES.medications,
    quantity: 8,
    unit: 'doses',
    reorderLevel: 25,
    supplier: 'Bluegrass Biologics',
    lotNumber: 'RV-8841',
    expirationDate: '2027-02-14',
    costPerUnit: 14.8
  },
  // WARNING: expires within 30 days.
  {
    id: 3,
    name: 'Dextrose 5% IV Bags',
    category: CATEGORIES.fluids,
    quantity: 46,
    unit: 'bags',
    reorderLevel: 15,
    supplier: 'Harbor Pharma',
    lotNumber: 'DX5-3308',
    expirationDate: expiringSoonDate,
    costPerUnit: 4.1
  },
  // CRITICAL: already expired.
  {
    id: 4,
    name: 'Heartworm Chewables',
    category: CATEGORIES.medications,
    quantity: 35,
    unit: 'boxes',
    reorderLevel: 10,
    supplier: 'Everline Labs',
    lotNumber: 'HW-1097',
    expirationDate: expiredDate,
    costPerUnit: 21.6
  },
  // CRITICAL: out of stock.
  {
    id: 5,
    name: 'IV Catheters 20G',
    category: CATEGORIES.medical,
    quantity: 0,
    unit: 'units',
    reorderLevel: 50,
    supplier: 'Alpine Medical',
    lotNumber: 'IVC-20-274',
    expirationDate: '2028-09-01',
    costPerUnit: 1.15
  },
  {
    id: 6,
    name: 'Gauze Rolls (4 in)',
    category: CATEGORIES.medical,
    quantity: 180,
    unit: 'rolls',
    reorderLevel: 60,
    supplier: 'Kettle Creek Supply',
    lotNumber: 'GZ-4552',
    expirationDate: '2029-05-01',
    costPerUnit: 0.55
  },
  {
    id: 7,
    name: 'Syringes 3 mL (Luer)',
    category: CATEGORIES.medical,
    quantity: 320,
    unit: 'units',
    reorderLevel: 120,
    supplier: 'PurePak Sterile',
    lotNumber: 'SY3-1186',
    expirationDate: '2028-11-01',
    costPerUnit: 0.18
  }
]

function isLowStock(row: TableRow<DemoInventoryItem>): boolean {
  return row.original.quantity <= row.original.reorderLevel
}

function isOutOfStock(row: TableRow<DemoInventoryItem>): boolean {
  return row.original.quantity === 0
}

function isExpired(row: TableRow<DemoInventoryItem>): boolean {
  if (!row.original.expirationDate) return false
  return new Date(row.original.expirationDate) < new Date()
}

function isExpiringSoon(row: TableRow<DemoInventoryItem>): boolean {
  if (!row.original.expirationDate) return false

  const expiration = new Date(row.original.expirationDate)
  const diffDays = (expiration.getTime() - Date.now()) / MS_PER_DAY
  return diffDays >= 0 && diffDays <= EXPIRING_SOON_WINDOW_DAYS
}

// Cells opt the whole row into the tint: the returned class has no styles of
// its own — the tr:has() rules in the style block below detect it.
function getRowStateFlag(
  row: TableRow<DemoInventoryItem> | null
): 'table-row-error' | 'table-row-warning' | undefined {
  if (row === null) return undefined

  if (isExpired(row)) return 'table-row-error'
  if (isOutOfStock(row)) return 'table-row-error'
  if (isExpiringSoon(row)) return 'table-row-warning'
  if (isLowStock(row)) return 'table-row-warning'

  return undefined
}

interface SortableColumn {
  getIsSorted: () => false | 'asc' | 'desc'
  clearSorting: () => void
  toggleSorting: (desc: boolean) => void
}

// Same render-function headers as the real page: a ghost button that opens
// an Asc/Desc dropdown and swaps its icon with the sort state.
function createColumnHeaderConfig(column: SortableColumn, label: string) {
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
          icon: 'i-lucide-arrow-down-wide-narrow',
          type: 'checkbox',
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
        label,
        icon: isSorted
          ? isSorted === 'asc'
            ? 'i-lucide-arrow-up-narrow-wide'
            : 'i-lucide-arrow-down-wide-narrow'
          : 'i-lucide-arrow-up-down',
        class: '-mx-2.5 data-[state=open]:bg-elevated cursor-pointer',
        'aria-label': `Sort by ${isSorted === 'asc' ? 'descending' : 'ascending'}`
      })
  )
}

// Full column set from the real page; later columns crop past the card edge.
const columns: TableColumn<DemoInventoryItem>[] = [
  { id: 'select' },
  { accessorKey: 'name', header: 'Item Name' },
  {
    accessorKey: 'category',
    header: ({ column }) => createColumnHeaderConfig(column, 'Category')
  },
  {
    accessorKey: 'quantity',
    header: ({ column }) => createColumnHeaderConfig(column, 'Quantity')
  },
  {
    accessorKey: 'reorderLevel',
    header: ({ column }) => createColumnHeaderConfig(column, 'Reorder Level')
  },
  { accessorKey: 'unit', header: 'Unit' },
  { accessorKey: 'supplier', header: 'Supplier' },
  { accessorKey: 'lotNumber', header: 'Lot No.' },
  {
    accessorKey: 'expirationDate',
    header: ({ column }) => createColumnHeaderConfig(column, 'Expiration Date')
  },
  {
    accessorKey: 'costPerUnit',
    header: ({ column }) => createColumnHeaderConfig(column, 'Cost Per Unit')
  },
  { id: 'actions' }
]

// The real app's per-row menu; all actions inert in the demo.
const rowDropdownItems: DropdownMenuItem[] = [
  { type: 'label', label: 'Actions' },
  { label: 'Edit', icon: 'i-lucide-edit-2' },
  { type: 'separator' },
  { label: 'Delete', color: 'error', icon: 'i-lucide-trash' }
]

const rowSelection = ref<Record<string, boolean>>({})
const sorting = ref<{ id: string; desc: boolean }[]>([])

// Pointer-following tooltip for flagged rows, anchored to a virtual element
// at the live pointer position — exactly like the real page.
const open = ref(false)
const tooltipMessage = ref('')
const tooltipMessageState = ref<'error' | 'warning' | null>(null)
const anchor = ref({ x: 0, y: 0 })

const popoverReference = computed(() => ({
  getBoundingClientRect: () =>
    ({
      width: 0,
      height: 0,
      left: anchor.value.x,
      right: anchor.value.x,
      top: anchor.value.y,
      bottom: anchor.value.y,
      ...anchor.value
    }) as DOMRect
}))

// Static class list (vs the real page's template string) so Tailwind
// generates border-error/border-warning for the popover panel.
const popoverClass = computed(() => [
  'bg-default/60 backdrop-blur-lg border',
  tooltipMessageState.value === 'error' ? 'border-error' : 'border-warning'
])

function updatePointerPosition(event: PointerEvent): void {
  anchor.value.x = event.clientX
  anchor.value.y = event.clientY
}

function onHover(_event: Event, row: TableRow<DemoInventoryItem> | null): void {
  if (row === null) {
    open.value = false
    tooltipMessage.value = ''
    tooltipMessageState.value = null
    return
  }

  if (isExpired(row)) {
    open.value = true
    tooltipMessage.value = 'This item has expired.'
    tooltipMessageState.value = 'error'
    return
  }

  if (isOutOfStock(row)) {
    open.value = true
    tooltipMessage.value = 'This item is out of stock.'
    tooltipMessageState.value = 'error'
    return
  }

  if (isExpiringSoon(row)) {
    open.value = true
    tooltipMessage.value = 'This item will expire soon.'
    tooltipMessageState.value = 'warning'
    return
  }

  if (isLowStock(row)) {
    open.value = true
    tooltipMessage.value = `${row.original.quantity} ${row.original.unit} remaining. Restock soon.`
    tooltipMessageState.value = 'warning'
    return
  }

  open.value = false
}

function onMouseLeave(): void {
  open.value = false
  tooltipMessage.value = ''
}

function formatExpirationDate(date?: string): string {
  if (!date) return ''

  const parsed = new Date(date)
  if (Number.isNaN(parsed.getTime())) return date

  // en-CA renders YYYY-MM-DD, matching the real page.
  return parsed.toLocaleDateString('en-CA')
}
</script>

<template>
  <DemoCanvas>
    <template #card>
      <!-- State tooltip that trails the pointer over flagged rows -->
      <UPopover
        :content="{ side: 'top', sideOffset: 16, updatePositionStrategy: 'always' }"
        :open="open"
        :reference="popoverReference"
        :class="popoverClass"
      >
        <template #content>
          <div
            v-if="open"
            class="p-4 flex gap-2 border"
            :class="tooltipMessageState === 'error'
              ? 'border-error-600 text-error-700 dark:border-error dark:text-error'
              : 'border-warning-600 text-warning-700 dark:border-warning dark:text-warning'"
          >
            <UIcon
              :name="tooltipMessageState === 'error' ? 'i-lucide-triangle-alert' : 'i-lucide-info'"
              class="size-6"
            />
            {{ tooltipMessage }}
          </div>
        </template>
      </UPopover>

      <!-- Flush with the card's top/left (1px offsets hide the table border
           under the card border); w-max lets the full 11-column layout run
           past the card edge so the crop reads as a screenshot. -->
      <div class="demo-inventory-rows absolute -top-px -left-px w-max">
        <UTable
          v-model:row-selection="rowSelection"
          v-model:sorting="sorting"
          :data="INVENTORY_ITEMS"
          :columns="columns"
          sticky
          class="bg-elevated/20 rounded-md border border-default"
          :ui="{ thead: 'bg-elevated' }"
          @hover="onHover"
          @pointermove="updatePointerPosition"
          @mouseleave="onMouseLeave"
        >
          <template #select-header="{ table }">
            <UCheckbox
              aria-label="Select all"
              class="cursor-pointer"
              :model-value="table.getIsAllPageRowsSelected() ? true : (table.getIsSomePageRowsSelected() ? 'indeterminate' : false)"
              @update:model-value="(value) => table.toggleAllPageRowsSelected(!!value)"
            />
          </template>

          <template #select-cell="{ row }">
            <UCheckbox
              aria-label="Select row"
              class="cursor-pointer"
              :model-value="row.getIsSelected()"
              @update:model-value="(value) => row.toggleSelected(!!value)"
            />
          </template>

          <!-- Flagged rows: red chip + red name text (even for warning tier);
               the chip also carries the row-state class -->
          <template #name-cell="{ row }">
            <UChip v-if="getRowStateFlag(row)" :class="getRowStateFlag(row)" color="error">
              <span class="pr-3 text-error">{{ row.original.name }}</span>
            </UChip>
            <span v-else>{{ row.original.name }}</span>
          </template>

          <template #category-cell="{ row }">
            <UBadge class="px-2 py-1 rounded text-xs font-medium" :class="row.original.category.color">
              {{ row.original.category.label }}
            </UBadge>
          </template>

          <template #quantity-cell="{ row }">
            <span :class="getRowStateFlag(row)">
              {{ row.original.quantity }}
            </span>
          </template>

          <template #reorderLevel-cell="{ row }">
            <span :class="getRowStateFlag(row)">
              {{ row.original.reorderLevel }}
            </span>
          </template>

          <template #expirationDate-cell="{ row }">
            <span :class="getRowStateFlag(row)">
              {{ formatExpirationDate(row.original.expirationDate) }}
            </span>
          </template>

          <template #costPerUnit-cell="{ row }">
            <span>${{ row.original.costPerUnit.toFixed(2) }}</span>
          </template>

          <template #actions-cell>
            <UDropdownMenu :items="rowDropdownItems">
              <UButton
                icon="i-lucide-ellipsis"
                color="neutral"
                variant="ghost"
                class="cursor-pointer"
                aria-label="Row actions"
              />
            </UDropdownMenu>
          </template>
        </UTable>
      </div>
    </template>
  </DemoCanvas>
</template>

<style>
/* Local replica of the real app's global row-state CSS (main.css @layer base):
   any cell carrying .table-row-warning/.table-row-error opts its whole <tr>
   into the tint via :has(), intensifying on hover. Values match the compiled
   output of bg-warning/10, bg-warning/15, etc. (color-mix in oklab), with
   !important to beat UTable's own hover styles — exactly like the app. */
.demo-inventory-rows tr {
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.demo-inventory-rows tr:has(.table-row-error) {
  background-color: color-mix(in oklab, var(--ui-error) 10%, transparent) !important;
}

.demo-inventory-rows tr:has(.table-row-error):hover {
  background-color: color-mix(in oklab, var(--ui-error) 15%, transparent) !important;
}

.demo-inventory-rows tr:has(.table-row-warning) {
  background-color: color-mix(in oklab, var(--ui-warning) 10%, transparent) !important;
}

.demo-inventory-rows tr:has(.table-row-warning):hover {
  background-color: color-mix(in oklab, var(--ui-warning) 15%, transparent) !important;
}

.dark .demo-inventory-rows tr:has(.table-row-error) {
  background-color: color-mix(in oklab, var(--ui-error) 5%, transparent) !important;
}

.dark .demo-inventory-rows tr:has(.table-row-error):hover {
  background-color: color-mix(in oklab, var(--ui-error) 10%, transparent) !important;
}

.dark .demo-inventory-rows tr:has(.table-row-warning) {
  background-color: color-mix(in oklab, var(--ui-warning) 5%, transparent) !important;
}

.dark .demo-inventory-rows tr:has(.table-row-warning):hover {
  background-color: color-mix(in oklab, var(--ui-warning) 10%, transparent) !important;
}
</style>
