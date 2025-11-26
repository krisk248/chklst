<template>
  <header class="h-16 bg-muted border-b border-border flex items-center px-8 ml-64">
    <div class="flex items-center justify-between w-full">
      <div>
        <h2 class="text-2xl font-bold text-foreground">{{ pageTitle }}</h2>
      </div>
      <div class="flex items-center gap-4">
        <button
          class="p-2 rounded-lg hover:bg-background transition-colors"
          title="Refresh"
        >
          <RefreshCw class="w-5 h-5" />
        </button>
        <button
          class="p-2 rounded-lg hover:bg-background transition-colors"
          title="Notifications"
        >
          <Bell class="w-5 h-5" />
        </button>
        <button
          class="p-2 rounded-lg hover:bg-background transition-colors"
          title="User Menu"
        >
          <User class="w-5 h-5" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { RefreshCw, Bell, User } from 'lucide-vue-next'

const route = useRoute()

const pageTitle = computed(() => {
  return (route.meta?.title as string) || 'Dashboard'
})
</script>
