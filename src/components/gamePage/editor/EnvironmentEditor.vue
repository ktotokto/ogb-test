<script setup>
import { computed } from 'vue'
import { useGameStore } from '@/stores/game'
import { Grid3X3, Ruler, Palette } from 'lucide-vue-next'

const gameStore = useGameStore()

const showGrid = computed({
  get: () => gameStore.settings?.gridEnabled ?? true,
  set: (value) => gameStore.updateSetting('gridEnabled', value)
})

const gridSize = computed({
  get: () => gameStore.settings?.gridSize ?? 50,
  set: (value) => gameStore.updateSetting('gridSize', value)
})

const backgroundColor = computed({
  get: () => gameStore.settings?.backgroundColor ?? '#0f172a',
  set: (value) => gameStore.updateSetting('backgroundColor', value)
})

const quickColors = ['#0f172a', '#1e293b', '#000000', '#111827', '#0f1f1a']
</script>

<template>
  <div class="space-y-3 p-1">

    <div
      class="flex items-center gap-3 p-3 bg-slate-800/40 border border-white/5 rounded-xl hover:border-white/10 transition-all duration-200">
      <div class="p-2 bg-violet-500/10 rounded-lg">
        <Grid3X3 class="w-5 h-5 text-violet-400" />
      </div>
      <div class="flex-1 min-w-0">
        <h4 class="text-sm font-medium text-white">Сетка</h4>
        <p class="text-xs text-slate-400 truncate">Отображение направляющих</p>
      </div>
      <label class="relative inline-flex items-center cursor-pointer">
        <input v-model="showGrid" type="checkbox" class="sr-only peer" />
        <div
          class="w-11 h-6 bg-slate-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-violet-600">
        </div>
      </label>
    </div>

    <div class="p-3 bg-slate-800/40 border border-white/5 rounded-xl hover:border-white/10 transition-all duration-200">
      <div class="flex items-center gap-3 mb-3">
        <div class="p-2 bg-violet-500/10 rounded-lg">
          <Ruler class="w-5 h-5 text-violet-400" />
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-medium text-white">Размер сетки</h4>
          <p class="text-xs text-slate-400 font-mono">{{ gridSize }} px</p>
        </div>
      </div>
      <input v-model="gridSize" type="range" min="10" max="100" step="10"
        class="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-violet-500" />
    </div>

    <div class="p-3 bg-slate-800/40 border border-white/5 rounded-xl hover:border-white/10 transition-all duration-200">
      <div class="flex items-center gap-3 mb-3">
        <div class="p-2 bg-violet-500/10 rounded-lg">
          <Palette class="w-5 h-5 text-violet-400" />
        </div>
        <div class="flex-1 min-w-0">
          <h4 class="text-sm font-medium text-white">Цвет фона</h4>
          <p class="text-xs text-slate-400 font-mono truncate">{{ backgroundColor }}</p>
        </div>
        <input v-model="backgroundColor" type="color"
          class="w-10 h-10 p-0 border-0 rounded-lg cursor-pointer bg-transparent"
          :style="{ backgroundColor: backgroundColor }" />
      </div>

      <div class="flex gap-2 mt-2">
        <button v-for="color in quickColors" :key="color" @click="backgroundColor = color"
          class="w-6 h-6 rounded-full border-2 transition-all hover:scale-110 active:scale-95"
          :class="backgroundColor === color ? 'border-white scale-110' : 'border-transparent'"
          :style="{ backgroundColor: color }" />
      </div>
    </div>

  </div>
</template>