<script setup>
import { onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['toggle-sidebar', 'zoom-in', 'zoom-out', 'reset-zoom', 'set-tool'])

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
        <span class="font-medium">Menu</span>
      </button>
    </div>

    <div class="flex items-center gap-2">
      <button @click="emit('zoom-out')"
        class="w-10 h-10 rounded-lg bg-slate-800/60 hover:bg-slate-700 text-slate-300 hover:text-white transition-all flex items-center justify-center border border-white/5">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
        </svg>
      </button>
      <button @click="emit('reset-zoom')"
        class="px-4 h-10 rounded-lg bg-slate-800/60 text-sm font-semibold text-slate-300 hover:text-white transition-all border border-white/5 min-w-[80px]">
        100%
      </button>
      <button @click="emit('zoom-in')"
        class="w-10 h-10 rounded-lg bg-slate-800/60 hover:bg-slate-700 text-slate-300 hover:text-white transition-all flex items-center justify-center border border-white/5">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </div>

    <div class="flex items-center gap-3">
      <button
        class="px-6 py-2.5 rounded-xl font-semibold transition-all bg-slate-800/60 hover:bg-slate-700 text-slate-300 hover:text-white border border-white/5 flex items-center gap-2.5">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
        </svg>
        <span>Roll Dice</span>
      </button>
      <button
        class="px-6 py-2.5 rounded-xl font-semibold transition-all bg-slate-800/60 hover:bg-slate-700 text-slate-300 hover:text-white border border-white/5 flex items-center gap-2.5">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <span>Draw Card</span>
      </button>
    </div>
  </footer>
</template>