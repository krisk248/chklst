<template>
  <div class="main-container">
    <Sidebar />
    <div class="flex-1 flex flex-col ml-48">
      <Header />
      <main class="flex-1 overflow-y-auto bg-background p-8">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
</script>
