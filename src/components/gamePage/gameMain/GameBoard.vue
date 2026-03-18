<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
    objects: {
        type: Array,
        default: () => [
            { id: 1, type: 'card', x: 200, y: 150, rotation: -5, label: 'Карта 1' },
            { id: 2, type: 'token', x: 400, y: 300, rotation: 0, label: 'token' },
            { id: 3, type: 'dice', x: 300, y: 200, rotation: 15, label: 'dice' },
        ]
    }
})

const emit = defineEmits(['object-select', 'object-move', 'board-click'])

const isDragging = ref(false)
const selectedObject = ref(null)

const handleMouseDown = (e, obj) => {
    e.stopPropagation()
    selectedObject.value = obj
    isDragging.value = true
    emit('object-select', obj)
}

const handleMouseMove = (e) => {
    if (!isDragging.value || !selectedObject.value) return
}

const handleMouseUp = () => {
    if (selectedObject.value) {
        emit('object-move', selectedObject.value)
    }
    isDragging.value = false
}

const handleBoardClick = (e) => {
    if (!e.target.closest('[data-game-object]')) {
        emit('board-click')
    }
}

onMounted(() => {
    window.addEventListener('mouseup', handleMouseUp)
})
onUnmounted(() => {
    window.removeEventListener('mouseup', handleMouseUp)
})
</script>

<template>
    <div ref="boardRef" class="w-full h-full relative cursor-crosshair" @click="handleBoardClick">
        <div v-for="obj in objects" :key="obj.id" :data-game-object="obj.id" :style="{
            left: `${obj.x}px`,
            top: `${obj.y}px`,
            transform: `rotate(${obj.rotation}deg)`,
        }" class="absolute cursor-grab active:cursor-grabbing select-none group"
            @mousedown="handleMouseDown($event, obj)" @mousemove="handleMouseMove">

            <div :class="[
                'relative p-3 rounded-xl shadow-lg transition-all',
                'bg-gradient-to-br from-slate-700 to-slate-800',
                'border-2 border-slate-600 hover:border-violet-500',
                selectedObject?.id === obj.id ? 'ring-2 ring-violet-400 ring-offset-2 ring-offset-slate-950' : '',
                'hover:shadow-xl hover:shadow-violet-500/10'
            ]">
                <div class="text-3xl text-center pointer-events-none">
                    {{ obj.type === 'card' ? 'card' : obj.type === 'dice' ? 'dice' : obj.label }}
                </div>

                <div v-if="obj.label && obj.type !== 'card'" class="mt-1 text-xs text-center text-slate-300">
                    {{ obj.label }}
                </div>

                <div v-if="selectedObject?.id === obj.id" class="absolute -inset-1 pointer-events-none">
                    <div
                        class="absolute -top-1.5 -left-1.5 w-3 h-3 bg-violet-400 rounded-full border-2 border-slate-900" />
                    <div
                        class="absolute -top-1.5 -right-1.5 w-3 h-3 bg-violet-400 rounded-full border-2 border-slate-900" />
                    <div
                        class="absolute -bottom-1.5 -left-1.5 w-3 h-3 bg-violet-400 rounded-full border-2 border-slate-900" />
                    <div
                        class="absolute -bottom-1.5 -right-1.5 w-3 h-3 bg-violet-400 rounded-full border-2 border-slate-900" />
                </div>

                <div
                    class="absolute -top-8 left-1/2 -translate-x-1/2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                        class="p-1 bg-slate-800 hover:bg-slate-700 rounded text-xs text-slate-300 hover:text-white shadow-lg">
                        редактировать
                    </button>
                    <button
                        class="p-1 bg-slate-800 hover:bg-slate-700 rounded text-xs text-slate-300 hover:text-white shadow-lg">
                        удалить
                    </button>
                </div>
            </div>
        </div>

        <div v-if="objects.length === 0" class="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div class="text-center text-slate-600">
                <p class="text-lg font-medium">Игровое поле пусто</p>
                <p class="text-sm">Добавьте объекты через панель справа</p>
            </div>
        </div>

        <div
            class="absolute bottom-3 right-5 px-2 py-1 bg-slate-900/80 backdrop-blur rounded text-xs font-mono text-slate-400">
            X: 0 Y: 0
        </div>
    </div>
</template>

<style scoped>
[data-game-object] {
    transition: transform 0.1s ease-out;
    will-change: transform;
}

.cursor-grabbing * {
    user-select: none;
    -webkit-user-select: none;
}
</style>