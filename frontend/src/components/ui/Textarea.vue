<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="text-sm font-medium text-gray-300">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :rows="rows"
      @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      :class="[
        'px-3 py-2 rounded-lg bg-[#404040] text-white border border-[#555555] placeholder-gray-500',
        'focus:outline-none focus:border-[#4a9eff] focus:ring-1 focus:ring-[#4a9eff]',
        'disabled:opacity-50 disabled:cursor-not-allowed resize-vertical',
        'font-mono text-sm',
        errorMessage && 'border-red-500 focus:border-red-500 focus:ring-red-500',
      ]"
    />
    <span v-if="errorMessage" class="text-xs text-red-500">
      {{ errorMessage }}
    </span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: string
  label?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  rows?: number
  errorMessage?: string
}

withDefaults(defineProps<Props>(), {
  rows: 4,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
