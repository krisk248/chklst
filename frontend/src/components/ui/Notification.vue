<template>
  <div
    v-if="appStore.hasNotification"
    :class="[
      'fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 flex items-start gap-3 max-w-md animate-slide-in',
      notificationClasses,
    ]"
  >
    <component :is="notificationIcon" class="w-5 h-5 flex-shrink-0 mt-0.5" />
    <div class="flex-1">
      <p class="text-sm font-medium">{{ appStore.notification.message }}</p>
    </div>
    <button
      @click="appStore.hideNotification"
      class="flex-shrink-0 ml-2 hover:opacity-70 transition-opacity"
    >
      <X class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '../../stores'
import {
  AlertCircle,
  CheckCircle,
  AlertTriangle,
  Info,
  X,
} from 'lucide-vue-next'

const appStore = useAppStore()

const notificationIcon = computed(() => {
  switch (appStore.notification.type) {
    case 'success':
      return CheckCircle
    case 'error':
      return AlertCircle
    case 'warning':
      return AlertTriangle
    default:
      return Info
  }
})

const notificationClasses = computed(() => {
  switch (appStore.notification.type) {
    case 'success':
      return 'bg-green-900 text-green-100 border border-green-700'
    case 'error':
      return 'bg-red-900 text-red-100 border border-red-700'
    case 'warning':
      return 'bg-yellow-900 text-yellow-100 border border-yellow-700'
    default:
      return 'bg-blue-900 text-blue-100 border border-blue-700'
  }
})
</script>

<style scoped>
@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-slide-in {
  animation: slide-in 0.3s ease-out;
}
</style>
