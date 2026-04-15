<script setup>
import { onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['toggle-sidebar', 'set-tool'])

const handleKeyDown = (event) => {
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return

  switch (event.key.toLowerCase()) {
    case 'v': emit('set-tool', 'select'); break
    case 'p': emit('set-tool', 'draw'); break
    case 'e': emit('set-tool', 'erase'); break
    case 'c': emit('set-tool', 'addCard'); break
    case 'h': emit('set-tool', 'pan'); break
  }
}

onMounted(() => window.addEventListener('keydown', handleKeyDown))
onUnmounted(() => window.removeEventListener('keydown', handleKeyDown))
</script>

<template>
  <footer class="h-16 bg-slate-900/90 backdrop-blur border-t border-white/10 flex items-center justify-between px-8">
    <div class="flex items-center gap-3">
      <button @click="emit('toggle-sidebar')"
        class="flex items-center gap-2.5 px-5 py-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-700 text-slate-300 hover:text-white transition-all border border-white/5">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <span class="font-medium">Меню</span>
      </button>
    </div>
  </footer>
</template>