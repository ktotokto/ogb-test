<script setup>
import { ref } from 'vue'

const activeTool = ref('select')

const tools = [
    { id: 'select', icon: 'cursor', label: 'Выделение', shortcut: 'V' },
    { id: 'pan', icon: 'hand', label: 'Перемещение', shortcut: 'H' },
    { id: 'draw', icon: 'pencil', label: 'Рисование', shortcut: 'P' },
    { id: 'text', icon: 'text', label: 'Текст', shortcut: 'T' },
    { id: 'shape', icon: 'square', label: 'Фигуры', shortcut: 'S' },
]

const actions = [
    { id: 'dice', label: 'Бросить кубик', hotkey: 'D' },
    { id: 'card', label: 'Взять карту', hotkey: 'C' },
    { id: 'undo', label: 'Отменить', hotkey: 'Ctrl+Z' },
    { id: 'redo', label: 'Повторить', hotkey: 'Ctrl+Y' },
]
</script>

<template>
    <div class="space-y-4">

        <div>
            <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-1">
                Инструменты
            </h3>
            <div class="grid grid-cols-5 gap-1">
                <button v-for="tool in tools" :key="tool.id" @click="activeTool = tool.id"
                    :title="`${tool.label} (${tool.shortcut})`" :class="[
                        'p-2.5 rounded-lg transition-all flex flex-col items-center gap-1',
                        activeTool === tool.id
                            ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/25'
                            : 'bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white'
                    ]">
                    <span class="text-[10px] font-mono text-slate-400">{{ tool.shortcut }}</span>
                </button>
            </div>
        </div>

        <div>
            <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-1">
                Действия
            </h3>
            <div class="space-y-1">
                <button v-for="action in actions" :key="action.id" :title="`${action.label} (${action.hotkey})`"
                    class="w-full flex items-center gap-3 p-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors group">
                    <span class="flex-1 text-left text-sm">{{ action.label }}</span>
                    <span class="text-[10px] font-mono text-slate-500 bg-slate-900 px-1.5 py-0.5 rounded">
                        {{ action.hotkey }}
                    </span>
                </button>
            </div>
        </div>

        <div class="pt-2 border-t border-slate-800">
            <div class="flex items-center justify-between">
                <span class="text-sm text-slate-400">Масштаб</span>
                <div class="flex items-center gap-1">
                    <button class="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                        </svg>
                    </button>
                    <span class="text-sm font-mono w-12 text-center">100%</span>
                    <button class="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                    </button>
                    <button class="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white ml-1"
                        title="Сбросить">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>

    </div>
</template>