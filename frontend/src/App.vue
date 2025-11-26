<template>
  <MainLayout>
    <RouterView />
    <Notification v-if="appStore.hasNotification" />
  </MainLayout>
</template>

<script setup lang="ts">
import { useAppStore } from './stores'
import MainLayout from './components/layout/MainLayout.vue'
import Notification from './components/ui/Notification.vue'
import { RouterView } from 'vue-router'

const appStore = useAppStore()

// WebSocket disabled - single user local app doesn't need real-time updates
</script>
