<script setup>
import { ref, computed } from 'vue'
import { useGameStore } from '@/stores/game'
import { Trees, Grid3X3, Palette } from 'lucide-vue-next'

const gameStore = useGameStore()

const showGrid = computed({
  get: () => gameStore.settings?.gridEnabled ?? true,
  set: (value) => gameStore.updateSetting('gridEnabled', value)
})

const gridSize = computed({
  get: () => gameStore.settings?.gridSize ?? 50,
  set: (value) => gameStore.updateSetting('gridSize', value)
})

const backgroundColor = ref(gameStore.settings?.backgroundColor || '#0f172a')
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3 p-3 bg-slate-800/40 border border-white/5 rounded-lg">
      <Grid3X3 class="w-5 h-5 text-violet-400" />
      <div class="flex-1">
        <h4 class="text-sm font-medium text-white">Сетка</h4>
        <p class="text-xs text-slate-400">Отображение сетки на поле</p>
      </div>
      <input
        v-model="showGrid"
        type="checkbox"
        class="w-5 h-5 rounded bg-slate-700 border-white/10"
      />
    </div>

    <div class="p-3 bg-slate-800/40 border border-white/5 rounded-lg">
      <div class="flex items-center gap-3 mb-3">
        <Palette class="w-5 h-5 text-violet-400" />
        <div>
          <h4 class="text-sm font-medium text-white">Размер сетки</h4>
          <p class="text-xs text-slate-400">{{ gridSize }}px</p>
        </div>
      </div>
      <input
        v-model="gridSize"
        type="range"
        min="10"
        max="100"
        step="10"
        class="w-full"
      />
    </div>
  </div>
</template>