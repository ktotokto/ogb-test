<script setup>
import { ref } from 'vue'
import { Dice5, SquareStack, Move, ZoomIn, ZoomOut } from 'lucide-vue-next'

const emit = defineEmits(['toggle-sidebar', 'zoom-in', 'zoom-out', 'reset-zoom', 'pan-mode'])
const activeButton = ref(null)
const panMode = ref(false)
</script>

<template>
  <footer class="h-16 glass-strong border-t border-white/10 flex items-center justify-between px-8">
    <!-- Left: Menu & Pan -->
    <div class="flex items-center gap-3">
      <button @click="emit('toggle-sidebar')" 
              class="flex items-center gap-2.5 px-5 py-2.5 rounded-xl glass-light hover:bg-white/5 text-slate-300 hover:text-white transition-all duration-300 border border-white/5">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
        <span class="font-medium">Меню</span>
      </button>
      
      <button @click="panMode = !panMode; emit('pan-mode', panMode)"
              :class="[
                'flex items-center gap-2.5 px-5 py-2.5 rounded-xl transition-all duration-300 border',
                panMode 
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/30' 
                  : 'glass-light hover:bg-white/5 text-slate-300 hover:text-white border-white/5'
              ]">
        <Move class="w-5 h-5" />
        <span class="font-medium">Перемещение</span>
      </button>
    </div>

    <!-- Center: Zoom Controls -->
    <div class="flex items-center gap-2">
      <button @click="emit('zoom-out')"
              class="w-10 h-10 rounded-lg glass-light hover:bg-white/5 text-slate-300 hover:text-white transition-all flex items-center justify-center border border-white/5">
        <ZoomOut class="w-4 h-4" />
      </button>
      
      <button @click="emit('reset-zoom')"
              class="px-4 h-10 rounded-lg glass text-sm font-semibold text-slate-300 hover:text-white transition-all border border-white/5 min-w-[80px]">
        100%
      </button>
      
      <button @click="emit('zoom-in')"
              class="w-10 h-10 rounded-lg glass-light hover:bg-white/5 text-slate-300 hover:text-white transition-all flex items-center justify-center border border-white/5">
        <ZoomIn class="w-4 h-4" />
      </button>
    </div>

    <!-- Right: Game Actions -->
    <div class="flex items-center gap-3">
      <button @click="activeButton = 'dice'"
              :class="[
                'px-6 py-2.5 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2.5',
                activeButton === 'dice' 
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/30 scale-105' 
                  : 'glass-light hover:bg-white/5 text-slate-300 hover:text-white border border-white/5'
              ]">
        <Dice5 class="w-5 h-5" />
        <span>Бросить кубик</span>
      </button>
      
      <button @click="activeButton = 'card'"
              :class="[
                'px-6 py-2.5 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2.5',
                activeButton === 'card' 
                  ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-lg shadow-violet-500/30 scale-105' 
                  : 'glass-light hover:bg-white/5 text-slate-300 hover:text-white border border-white/5'
              ]">
        <SquareStack class="w-5 h-5" />
        <span>Взять карту</span>
      </button>
    </div>
  </footer>
</template>