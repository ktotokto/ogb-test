<script setup>
import { ref } from 'vue'
import { MousePointer2, Hand, Pencil, Type, Square, Eraser } from 'lucide-vue-next'

const activeTool = ref('select')

const tools = [
  { id: 'select', icon: MousePointer2, label: 'Выбор', shortcut: 'V', color: 'from-violet-500 to-purple-600' },
  { id: 'pan', icon: Hand, label: 'Перемещение', shortcut: 'H', color: 'from-cyan-500 to-blue-600' },
  { id: 'draw', icon: Pencil, label: 'Рисование', shortcut: 'P', color: 'from-amber-500 to-orange-600' },
  { id: 'text', icon: Type, label: 'Текст', shortcut: 'T', color: 'from-emerald-500 to-teal-600' },
  { id: 'shape', icon: Square, label: 'Фигуры', shortcut: 'S', color: 'from-pink-500 to-rose-600' },
  { id: 'erase', icon: Eraser, label: 'Ластик', shortcut: 'E', color: 'from-slate-500 to-gray-600' }
]
</script>

<template>
  <div class="w-80 p-6">
    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
      <span class="w-1 h-4 bg-gradient-to-b from-violet-500 to-cyan-500 rounded-full"></span>
      В разработке... 
    </h3>
    
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
          <span class="text-[10px] opacity-60 font-mono"></span>
        </div>
        <span class="text-sm font-medium block"></span>
        
        <div v-if="activeTool === tool.id" class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-white/80"></div>
      </button>
    </div>


  </div>
</template>