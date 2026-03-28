<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useGameBoardPan } from '@/composables/useGameBoardPan'
import GameObject from './GameObject.vue'
import { ZoomIn, ZoomOut, Maximize, Move } from 'lucide-vue-next'

const gameStore = useGameStore()
const userStore = useUserStore()

const boardRef = ref(null)
const boardContainerRef = ref(null)
const selectedObjects = ref(new Set())
const showGrid = ref(true)
const gridSize = ref(50)

// Используем pan composable
const {
    isPanning,
    panOffset,
    zoom,
    zoomIn,
    zoomOut,
    resetZoom,
    setZoom
} = useGameBoardPan(boardRef, {
    enabled: true,
    onPanStart: () => console.log('Pan start'),
    onPanMove: (event, offset) => {
        // Можно обновлять UI если нужно
    },
    onPanEnd: () => console.log('Pan end')
})

const currentUser = computed(() => userStore.currentUser)
const isAdmin = computed(() => gameStore.isAdmin)

// Mock данных
const objects = ref([
    {
        id: 'obj_1',
        type: 'card',
        label: 'Карта атаки',
        position: { x: 150, y: 200 },
        width: 120,
        height: 180,
        rotation: 0,
        owner: 'user_123',
        resizable: true
    },
    {
        id: 'obj_2',
        type: 'dice',
        label: 'D6',
        position: { x: 400, y: 300 },
        width: 60,
        height: 60,
        rotation: 15,
        owner: 'user_123',
        resizable: false
    },
    {
        id: 'obj_3',
        type: 'token',
        label: 'Герой',
        position: { x: 600, y: 150 },
        width: 80,
        height: 80,
        rotation: 0,
        owner: 'user_456',
        resizable: true
    }
])

// Обработчики
const handleObjectSelect = (object) => {
    selectedObjects.value.clear()
    selectedObjects.value.add(object.id)
}

const handleObjectMove = ({ objectId, position }) => {
    const obj = objects.value.find(o => o.id === objectId)
    if (obj) obj.position = position
}

const handleObjectDelete = (objectId) => {
    objects.value = objects.value.filter(o => o.id !== objectId)
    selectedObjects.value.delete(objectId)
}

const handleObjectDuplicate = (object) => {
    const newObject = {
        ...object,
        id: `obj_${Date.now()}`,
        position: {
            x: object.position.x + 20,
            y: object.position.y + 20
        }
    }
    objects.value.push(newObject)
}

const handleObjectRotate = ({ objectId, rotation }) => {
    const obj = objects.value.find(o => o.id === objectId)
    if (obj) obj.rotation = rotation
}

const handleBoardClick = (event) => {
    if (event.target === boardRef.value || event.target.classList.contains('board-background')) {
        selectedObjects.value.clear()
    }
}

// Grid styles
const gridStyles = computed(() => ({
    backgroundImage: showGrid.value ? `
    linear-gradient(rgba(139, 92, 246, 0.15) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139, 92, 246, 0.15) 1px, transparent 1px)
  ` : 'none',
    backgroundSize: `${gridSize.value}px ${gridSize.value}px`
}))

// Координаты мыши
const mousePosition = ref({ x: 0, y: 0 })

const handleMouseMove = (event) => {
    if (boardRef.value) {
        const rect = boardRef.value.getBoundingClientRect()
        mousePosition.value = {
            x: Math.round((event.clientX - rect.left - panOffset.value.x) / zoom.value),
            y: Math.round((event.clientY - rect.top - panOffset.value.y) / zoom.value)
        }
    }
}

defineExpose({
  zoomIn,
  zoomOut,
  resetZoom,
  setZoom,
  panOffset,
  zoom
})


</script>

<template>
    <div class="w-full h-full relative bg-slate-950 overflow-hidden">
        <!-- Board Container -->
        <div ref="boardContainerRef" class="absolute inset-0 board-pan-area cursor-default" @click="handleBoardClick"
            @mousemove="handleMouseMove">
            <!-- Transformable Board -->
            <div ref="boardRef" class="absolute min-w-full min-h-full board-background" :style="[
                gridStyles,
                {
                    transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoom})`,
                    transformOrigin: '0 0'
                }
            ]">
                <!-- Game Objects -->
                <GameObject v-for="obj in objects" :key="obj.id" :object="obj"
                    :is-selected="selectedObjects.has(obj.id)" :is-draggable="true"
                    :is-resizable="obj.resizable !== false" :zoom="zoom" :grid-size="gridSize" :snap-to-grid="false"
                    @select="handleObjectSelect" @move="handleObjectMove" @delete="handleObjectDelete"
                    @duplicate="handleObjectDuplicate" @rotate="handleObjectRotate" />
            </div>
        </div>

        <!-- Pan Indicator -->
        <div v-if="isPanning"
            class="fixed top-24 left-1/2 -translate-x-1/2 px-4 py-2 bg-violet-600/90 backdrop-blur rounded-full text-sm text-white pointer-events-none z-50 animate-pulse shadow-lg">
            <Move class="w-4 h-4 inline mr-2" />
            Перемещение поля
        </div>

        <!-- Zoom Controls -->
        <div class="absolute bottom-24 right-6 flex flex-col gap-2">
            <button @click="zoomIn()"
                class="w-12 h-12 rounded-xl glass-strong hover:bg-white/10 flex items-center justify-center text-white hover:text-violet-400 transition-all shadow-lg hover:scale-110 active:scale-95 border border-white/10"
                title="Приблизить (+)">
                <ZoomIn class="w-5 h-5" />
            </button>

            <button @click="resetZoom()"
                class="w-12 h-12 rounded-xl glass-strong hover:bg-white/10 flex items-center justify-center text-white hover:text-cyan-400 transition-all shadow-lg hover:scale-110 active:scale-95 border border-white/10 text-xs font-bold"
                title="Сбросить (Ctrl+0)">
                {{ Math.round(zoom * 100) }}%
            </button>

            <button @click="zoomOut()"
                class="w-12 h-12 rounded-xl glass-strong hover:bg-white/10 flex items-center justify-center text-white hover:text-violet-400 transition-all shadow-lg hover:scale-110 active:scale-95 border border-white/10"
                title="Отдалить (-)">
                <ZoomOut class="w-5 h-5" />
            </button>
        </div>

        <!-- Coordinates Display -->
        <div
            class="absolute bottom-6 right-6 px-4 py-2 rounded-xl glass-strong border border-white/10 text-sm font-mono">
            <span class="text-slate-400">X: </span>
            <span class="text-violet-400 font-semibold">{{ mousePosition.x }}</span>
            <span class="text-slate-500 mx-2">|</span>
            <span class="text-slate-400">Y: </span>
            <span class="text-cyan-400 font-semibold">{{ mousePosition.y }}</span>
            <span class="text-slate-500 mx-2">|</span>
            <span class="text-slate-400">Z: </span>
            <span class="text-emerald-400 font-semibold">{{ Math.round(zoom * 100) }}%</span>
        </div>

        <!-- Help Tooltip -->
        <div
            class="absolute bottom-6 left-6 px-4 py-3 rounded-xl glass-strong border border-white/10 text-xs space-y-1">
            <div class="flex items-center gap-2 text-slate-300">
                <kbd class="px-2 py-1 rounded bg-slate-800 font-mono text-violet-400">Alt</kbd>
                <span>+ Drag = Перемещение поля</span>
            </div>
            <div class="flex items-center gap-2 text-slate-300">
                <kbd class="px-2 py-1 rounded bg-slate-800 font-mono text-violet-400">Ctrl</kbd>
                <span>+ Wheel = Зум</span>
            </div>
            <div class="flex items-center gap-2 text-slate-300">
                <kbd class="px-2 py-1 rounded bg-slate-800 font-mono text-violet-400">↑↓←→</kbd>
                <span>= Перемещение</span>
            </div>
        </div>
    </div>
</template>

<style scoped>
.board-background {
    background-color: #0f172a;
    min-width: 2000px;
    min-height: 2000px;
    will-change: transform;
}

/* Grid pattern */
.board-background {
    background-image:
        linear-gradient(rgba(139, 92, 246, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(139, 92, 246, 0.1) 1px, transparent 1px);
    background-size: 50px 50px;
}
</style>