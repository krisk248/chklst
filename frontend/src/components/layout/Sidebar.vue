<template>
  <aside
    class="w-48 bg-muted border-r border-border flex flex-col h-screen fixed left-0 top-0"
  >
    <!-- Logo/Header -->
    <div class="p-4 border-b border-border">
      <h1 class="text-xl font-bold text-accent">chklst</h1>
      <p class="text-xs text-gray-400 mt-1">Deployment Tracker</p>
    </div>

    <!-- Navigation Links -->
    <nav class="flex-1 overflow-y-auto px-2 py-3">
      <ul class="space-y-1">
        <li
          v-for="item in menuItems"
          :key="item.path"
        >
          <RouterLink
            :to="item.path"
            :class="[
              'sidebar-link',
              $route.path === item.path && 'active',
            ]"
          >
            <component :is="item.icon" class="w-4 h-4" />
            <span class="text-sm">{{ item.label }}</span>
          </RouterLink>
        </li>
      </ul>
    </nav>

    <!-- Footer -->
    <div class="p-4 border-t border-border text-xs text-gray-400">
      <p>v3.0.0</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import {
  Home,
  Folder,
  BookOpen,
  Clock,
  BarChart3,
  Settings,
  Info,
  Download,
  TrendingUp,
} from 'lucide-vue-next'

useRoute()

const menuItems = [
  { path: '/deployment', label: 'Deployment', icon: Home },
  { path: '/projects', label: 'Projects', icon: Folder },
  { path: '/library', label: 'Library', icon: BookOpen },
  { path: '/history', label: 'History', icon: Clock },
  { path: '/reports', label: 'Reports', icon: BarChart3 },
  { path: '/export', label: 'Export', icon: Download },
  { path: '/analysis', label: 'Analysis', icon: TrendingUp },
  { path: '/settings', label: 'Settings', icon: Settings },
  { path: '/about', label: 'About', icon: Info },
]
</script>
