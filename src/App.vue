<script setup lang="ts">
import AppHeader from './components/layout/AppHeader.vue'
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex flex-col">
    <AppHeader />
    <main class="flex-1">
      <RouterView />
    </main>
  </div>
</template>