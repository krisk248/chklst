<template>
  <button
    :type="type"
    :class="[
      'px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2',
      variantClasses,
      sizeClasses,
      disabled && 'opacity-50 cursor-not-allowed',
    ]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  type: 'button',  // IMPORTANT: Default to 'button' to prevent form submission
})

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'secondary':
      return 'bg-[#404040] text-white hover:bg-[#555555]'
    case 'danger':
      return 'bg-red-600 text-white hover:bg-red-700'
    case 'success':
      return 'bg-green-600 text-white hover:bg-green-700'
    case 'ghost':
      return 'bg-transparent text-white border border-[#555555] hover:bg-[#404040]'
    default:
      return 'bg-[#4a9eff] text-white hover:bg-[#3a8eef]'
  }
})

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'text-sm px-3 py-1.5'
    case 'lg':
      return 'text-lg px-6 py-3'
    default:
      return 'text-base'
  }
})
</script>
