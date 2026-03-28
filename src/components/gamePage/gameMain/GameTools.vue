<script setup>
import { ref } from 'vue'
import { MousePointer2, Hand, Pencil, Type, Square, Eraser, Undo2, Redo2 } from 'lucide-vue-next'

const activeTool = ref('select')

const tools = [
  { id: 'select', icon: MousePointer2, label: 'Выбор', shortcut: 'V', color: 'from-violet-500 to-purple-600' },
  { id: 'pan', icon: Hand, label: 'Перемещение', shortcut: 'H', color: 'from-cyan-500 to-blue-600' },
  { id: 'draw', icon: Pencil, label: 'Рисование', shortcut: 'P', color: 'from-amber-500 to-orange-600' },
  { id: 'text', icon: Type, label: 'Текст', shortcut: 'T', color: 'from-emerald-500 to-teal-600' },
  { id: 'shape', icon: Square, label: 'Фигуры', shortcut: 'S', color: 'from-pink-500 to-rose-600' },
  { id: 'erase', icon: Eraser, label: 'Ластик', shortcut: 'E', color: 'from-slate-500 to-gray-600' }
]

const actions = [
  { id: 'undo', icon: Undo2, label: 'Отменить', shortcut: 'Ctrl+Z' },
  { id: 'redo', icon: Redo2, label: 'Повторить', shortcut: 'Ctrl+Y' }
]
</script>

<template>
  <div class="w-80 p-6">
    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
      <span class="w-1 h-4 bg-gradient-to-b from-violet-500 to-cyan-500 rounded-full"></span>
      Инструменты
    </h3>
    
    <!-- Tools Grid - 2 columns for better spacing -->
    <div class="grid grid-cols-2 gap-3 mb-6">
      <button v-for="tool in tools" :key="tool.id"
              @click="activeTool = tool.id"
              :class="[
                'relative p-4 rounded-xl transition-all duration-300 group text-left',
                activeTool === tool.id 
                  ? `bg-gradient-to-br ${tool.color} text-white shadow-lg scale-[1.02]` 
                  : 'glass-light hover:bg-white/5 text-slate-300 hover:text-white border border-white/5'
              ]">
        <div class="flex items-start justify-between mb-2">
          <component :is="tool.icon" class="w-6 h-6" />
          <span class="text-[10px] opacity-60 font-mono">{{ tool.shortcut }}</span>
        </div>
        <span class="text-sm font-medium block">{{ tool.label }}</span>
        
        <!-- Active indicator -->
        <div v-if="activeTool === tool.id" class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-white/80"></div>
      </button>
    </div>

    <!-- Actions -->
    <div class="mb-6">
      <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Действия</h4>
      <div class="space-y-2">
        <button v-for="action in actions" :key="action.id"
                class="w-full flex items-center gap-3 p-3 rounded-lg glass-light hover:bg-white/5 text-slate-300 hover:text-white transition-all duration-300 group border border-white/5">
          <component :is="action.icon" class="w-5 h-5 group-hover:scale-110 transition-transform" />
          <span class="text-sm flex-1 text-left font-medium">{{ action.label }}</span>
          <span class="text-[10px] text-slate-500 font-mono bg-slate-800/50 px-2 py-1 rounded">{{ action.shortcut }}</span>
        </button>
      </div>
    </div>

    <!-- Zoom Controls -->
    <div class="pt-6 border-t border-white/10">
      <div class="flex items-center justify-between mb-3">
        <span class="text-xs font-medium text-slate-400">Масштаб</span>
        <span class="text-sm font-mono font-semibold text-violet-400">100%</span>
      </div>
      <div class="flex items-center gap-2">
        <button class="flex-1 py-3 rounded-lg glass-light hover:bg-white/5 text-slate-300 hover:text-white transition-colors text-xl font-semibold hover:scale-105 active:scale-95">−</button>
        <button class="flex-1 py-3 rounded-lg glass text-sm font-semibold text-slate-300 hover:text-white transition-colors hover:bg-white/5">100%</button>
        <button class="flex-1 py-3 rounded-lg glass-light hover:bg-white/5 text-slate-300 hover:text-white transition-colors text-xl font-semibold hover:scale-105 active:scale-95">+</button>
      </div>
      <button class="w-full mt-3 py-2.5 rounded-lg glass-light hover:bg-white/5 text-xs text-slate-400 hover:text-slate-300 transition-colors">
        Сбросить масштаб
      </button>
    </div>
  </div>
</template>