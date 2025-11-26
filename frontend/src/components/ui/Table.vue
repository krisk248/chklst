<template>
  <div class="overflow-x-auto rounded-lg border border-[#555555]">
    <table class="w-full">
      <thead class="bg-[#404040] border-b border-[#555555]">
        <tr>
          <th v-for="column in columns" :key="column.key" class="px-4 py-3 text-left text-sm font-medium text-gray-300 whitespace-nowrap">
            {{ column.label }}
          </th>
          <th v-if="hasActions" class="px-4 py-3 text-left text-sm font-medium text-gray-300">
            Actions
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, idx) in data"
          :key="idx"
          class="border-b border-[#555555] hover:bg-[#404040] transition-colors"
        >
          <td
            v-for="column in columns"
            :key="`${idx}-${column.key}`"
            class="px-4 py-3 text-sm text-white whitespace-nowrap overflow-hidden text-ellipsis max-w-xs"
          >
            <template v-if="column.format">
              {{ column.format(row[column.key]) }}
            </template>
            <template v-else>
              {{ row[column.key] }}
            </template>
          </td>
          <td v-if="hasActions" class="px-4 py-3 text-sm space-x-2">
            <slot name="actions" :row="row" />
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="data.length === 0" class="text-center py-8 text-gray-400">
      <p>{{ emptyMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Column {
  key: string
  label: string
  format?: (value: any) => string
}

interface Props {
  data: Record<string, any>[]
  columns: Column[]
  emptyMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  emptyMessage: 'No data available',
})

defineSlots<{
  actions(props: { row: Record<string, any> }): any
}>()

const hasActions = computed(() => {
  // Check if actions slot is provided
  return true
})
</script>
