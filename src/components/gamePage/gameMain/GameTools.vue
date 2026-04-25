<script setup>
import { ref } from 'vue'

const activeTool = ref('select')

const tools = [
  { id: 'select', label: 'Колоды', color: 'from-violet-500 to-purple-600' },
  { id: 'pan', label: 'Объекты', color: 'from-cyan-500 to-blue-600' },
  { id: 'draw', label: 'Шаблоны игр', color: 'from-amber-500 to-orange-600' },
  { id: 'text', label: 'Окружение', color: 'from-emerald-500 to-teal-600' }
]
</script>

<template>
  <div class="w-80 p-6">
    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
      <span class="w-1 h-4 bg-gradient-to-b from-violet-500 to-cyan-500 rounded-full"></span>
      Редактор
    </h3>

    <div class="grid grid-cols-2 gap-3 mb-6">
      <button v-for="tool in tools" :key="tool.id" @click="activeTool = tool.id" :class="[
        'relative p-4 rounded-xl transition-all duration-300 group text-left',
        activeTool === tool.id
          ? `bg-gradient-to-br ${tool.color} text-white shadow-lg scale-[1.02]`
          : 'glass-light hover:bg-white/5 text-slate-300 hover:text-white border border-white/5'
      ]">
        <span class="text-sm font-medium block">{{ tool.label }}</span>

      </button>
    </div>


  </div>
</template>