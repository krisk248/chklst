<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="text-sm font-medium text-gray-300">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <select
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      :class="[
        'px-3 py-2 rounded-lg bg-[#404040] text-white border border-[#555555]',
        'focus:outline-none focus:border-[#4a9eff] focus:ring-1 focus:ring-[#4a9eff]',
        'disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer',
        'appearance-none pr-8',
        errorMessage && 'border-red-500 focus:border-red-500 focus:ring-red-500',
      ]"
      :style="{
        backgroundImage: `url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2212%22 height=%228%22 viewBox=%220 0 12 8%22%3E%3Cpath fill=%22%23ffffff%22 d=%22M0 0l6 8 6-8z%22/%3E%3C/svg%3E')`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'right 0.5rem center',
        backgroundSize: '1.2em auto',
        paddingRight: '2rem',
      }"
    >
      <option v-if="!modelValue" value="" disabled>{{ placeholder || 'Select...' }}</option>
      <option v-for="option in options" :key="option" :value="option">
        {{ option }}
      </option>
    </select>
    <span v-if="errorMessage" class="text-xs text-red-500">
      {{ errorMessage }}
    </span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: string
  options: string[]
  label?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  errorMessage?: string
}

withDefaults(defineProps<Props>(), {})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
