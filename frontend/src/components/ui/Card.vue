<template>
  <div
    :class="[
      'rounded-lg border border-[#555555] bg-[#2b2b2b] overflow-hidden',
      padding,
    ]"
  >
    <div v-if="title" class="border-b border-[#555555] pb-4 mb-4">
      <h2 class="text-lg font-bold text-white">{{ title }}</h2>
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  padding?: string
}

withDefaults(defineProps<Props>(), {
  padding: 'p-6',
})
</script>
