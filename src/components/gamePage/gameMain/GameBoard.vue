<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useGameBoardPan } from '@/composables/useGameBoardPan'
import GameObject from './GameObject.vue'

const gameStore = useGameStore()
const userStore = useUserStore()

const boardRef = ref(null)
const drawCanvasRef = ref(null)
const selectedObjects = ref(new Set())
const showGrid = ref(true)
const gridSize = ref(50)

const currentTool = ref('select')
const brushColor = ref('#8b5cf6')
const brushSize = ref(3)
const isDrawing = ref(false)
const lastPoint = ref(null)

const isSelecting = ref(false)
const selectionStart = ref({ x: 0, y: 0 })
const selectionEnd = ref({ x: 0, y: 0 })
const selectionBox = ref(null)

const {
  isPanning,
  panOffset,
  zoom,
  zoomIn,
  zoomOut,
  resetZoom,
  setZoom
} = useGameBoardPan(boardRef, { enabled: true })

const currentUser = computed(() => userStore.currentUser)

const objects = ref([])
const drawings = ref([])

const cardDeck = [
  { id: 'card_attack', name: 'Attack', type: 'attack' },
  { id: 'card_defense', name: 'Defense', type: 'defense' },
  { id: 'card_magic', name: 'Magic', type: 'magic' },
  { id: 'card_heal', name: 'Heal', type: 'heal' },
]

const showCardPanel = ref(false)
const selectedCard = ref(null)

const gridStyles = computed(() => ({
  backgroundImage: showGrid.value ? `
    linear-gradient(rgba(139, 92, 246, 0.15) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139, 92, 246, 0.15) 1px, transparent 1px)
  ` : 'none',
  backgroundSize: `${gridSize.value}px ${gridSize.value}px`,
  backgroundRepeat: 'repeat',
  width: '100000px',
  height: '100000px',
  transform: `translate(${panOffset.value.x}px, ${panOffset.value.y}px) scale(${zoom.value})`,
  transformOrigin: '0 0'
}))

const cursorStyle = computed(() => {
  const cursors = {
    select: 'default',
    pan: 'grab',
    draw: 'crosshair',
    erase: 'cell',
    addCard: 'copy'
  }
  return cursors[currentTool.value] || 'default'
})

const initDrawCanvas = () => {
  if (!drawCanvasRef.value) return
  const canvas = drawCanvasRef.value
  canvas.width = 100000
  canvas.height = 100000
  const ctx = canvas.getContext('2d')
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
}

const getBoardCoordinates = (event) => {
  if (!boardRef.value) return { x: 0, y: 0 }
  const rect = boardRef.value.getBoundingClientRect()
  return {
    x: Math.round((event.clientX - rect.left - panOffset.value.x) / zoom.value),
    y: Math.round((event.clientY - rect.top - panOffset.value.y) / zoom.value)
  }
}

const startDrawing = (event) => {
  if (currentTool.value !== 'draw' || !drawCanvasRef.value) return
  event.preventDefault()
  isDrawing.value = true
  lastPoint.value = getBoardCoordinates(event)
  const ctx = drawCanvasRef.value.getContext('2d')
  ctx.beginPath()
  ctx.moveTo(lastPoint.value.x, lastPoint.value.y)
}

const draw = (event) => {
  if (!isDrawing.value || currentTool.value !== 'draw' || !drawCanvasRef.value) return
  event.preventDefault()
  const point = getBoardCoordinates(event)
  const ctx = drawCanvasRef.value.getContext('2d')
  ctx.strokeStyle = brushColor.value
  ctx.lineWidth = Math.max(1, brushSize.value / zoom.value)
  ctx.lineTo(point.x, point.y)
  ctx.stroke()
  drawings.value.push({
    id: `draw_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    type: 'line',
    from: { ...lastPoint.value },
    to: { ...point },
    color: brushColor.value,
    size: brushSize.value
  })
  lastPoint.value = point
}

const stopDrawing = () => {
  if (!isDrawing.value) return
  isDrawing.value = false
  lastPoint.value = null
  if (drawCanvasRef.value) {
    drawCanvasRef.value.getContext('2d').closePath()
  }
}

const eraseAtPoint = (event) => {
  if (currentTool.value !== 'erase') return
  const point = getBoardCoordinates(event)
  const eraseRadius = 30 / zoom.value
  const beforeCount = drawings.value.length
  drawings.value = drawings.value.filter(d => {
    const dist = Math.sqrt(
      Math.pow(d.to.x - point.x, 2) +
      Math.pow(d.to.y - point.y, 2)
    )
    return dist > eraseRadius
  })
  if (drawings.value.length !== beforeCount) {
    redrawCanvas()
  }
}

const redrawCanvas = () => {
  if (!drawCanvasRef.value) return
  const canvas = drawCanvasRef.value
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  drawings.value.forEach(d => {
    ctx.beginPath()
    ctx.moveTo(d.from.x, d.from.y)
    ctx.lineTo(d.to.x, d.to.y)
    ctx.strokeStyle = d.color
    ctx.lineWidth = Math.max(1, d.size / zoom.value)
    ctx.stroke()
  })
}

const addCardToBoard = (card, event) => {
  const pos = getBoardCoordinates(event)
  const newCard = {
    id: `card_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    type: 'card',
    label: card.name,
    position: { x: pos.x - 60, y: pos.y - 90 },
    width: 120,
    height: 180,
    rotation: 0,
    owner: currentUser.value?.id || 'user',
    resizable: true,
    cardData: card
  }
  objects.value.push(newCard)
  showCardPanel.value = false
  currentTool.value = 'select'
}

const handleBoardMouseDown = (event) => {
  if (event.target.closest('.game-object')) return
  if (event.target.closest('.toolbar')) return

  if (currentTool.value === 'select') {
    startSelection(event)
  } else if (currentTool.value === 'draw') {
    startDrawing(event)
  } else if (currentTool.value === 'erase') {
    eraseAtPoint(event)
  } else if (currentTool.value === 'addCard' && selectedCard.value) {
    addCardToBoard(selectedCard.value, event)
  }
}

const handleBoardMouseMove = (event) => {
  if (currentTool.value === 'select') {
    updateSelection(event)
  } else if (currentTool.value === 'draw') {
    draw(event)
  } else if (currentTool.value === 'erase') {
    eraseAtPoint(event)
  }
}

const handleBoardMouseUp = () => {
  stopDrawing()
  endSelection()
}

const handleObjectMove = ({ objectId, position }) => {
  const obj = objects.value.find(o => o.id === objectId)
  if (obj) {
    obj.position = position
    // Перемещать все выделенные объекты относительно первого
    if (selectedObjects.value.has(objectId)) {
      const offsetX = position.x - (obj.lastPosition?.x || position.x)
      const offsetY = position.y - (obj.lastPosition?.y || position.y)
      objects.value.forEach(o => {
        if (selectedObjects.value.has(o.id) && o.id !== objectId) {
          o.position.x += offsetX
          o.position.y += offsetY
          o.lastPosition = { ...o.position }
        }
      })
    }
    obj.lastPosition = { ...position }
  }
}


const selectCardToAdd = (card) => {
  selectedCard.value = card
  currentTool.value = 'addCard'
  showCardPanel.value = false
}

const handleObjectSelect = (object, event) => {
  if (event?.ctrlKey || event?.metaKey) {
    if (selectedObjects.value.has(object.id)) {
      selectedObjects.value.delete(object.id)
    } else {
      selectedObjects.value.add(object.id)
    }
  } else if (event?.shiftKey && selectedObjects.value.size > 0) {
    const firstId = Array.from(selectedObjects.value)[0]
    const firstIndex = objects.value.findIndex(o => o.id === firstId)
    const currentIndex = objects.value.findIndex(o => o.id === object.id)
    const start = Math.min(firstIndex, currentIndex)
    const end = Math.max(firstIndex, currentIndex)
    selectedObjects.value.clear()
    for (let i = start; i <= end; i++) {
      selectedObjects.value.add(objects.value[i].id)
    }
  } else {
    selectedObjects.value.clear()
    selectedObjects.value.add(object.id)
  }
}

const handleObjectDelete = (objectId) => {
  if (objectId) {
    objects.value = objects.value.filter(o => o.id !== objectId)
    selectedObjects.value.delete(objectId)
  } else {
    const idsToDelete = Array.from(selectedObjects.value)
    objects.value = objects.value.filter(o => !selectedObjects.value.has(o.id))
    selectedObjects.value.clear()
  }
}

const handleObjectDuplicate = (object) => {
  objects.value.push({
    ...object,
    id: `obj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    position: { x: object.position.x, y: object.position.y}
  })
}

const handleObjectRotate = ({ objectId, rotation }) => {
  if (objectId) {
    const obj = objects.value.find(o => o.id === objectId)
    if (obj) obj.rotation = rotation
  } else {
    selectedObjects.value.forEach(id => {
      const obj = objects.value.find(o => o.id === id)
      if (obj) obj.rotation = (obj.rotation || 0) + 90
    })
  }
}

const handleBoardClick = (event) => {
  if (event.target === boardRef.value || event.target.classList.contains('board-background')) {
    if (!isSelecting.value) {
      selectedObjects.value.clear()
    }
  }
}

const startSelection = (event) => {
  if (currentTool.value !== 'select') return
  if (event.target.closest('.game-object')) return

  const pos = getBoardCoordinates(event)
  isSelecting.value = true
  selectionStart.value = { x: pos.x, y: pos.y }
  selectionEnd.value = { x: pos.x, y: pos.y }
}

const updateSelection = (event) => {
  if (!isSelecting.value) return
  const pos = getBoardCoordinates(event)
  selectionEnd.value = { x: pos.x, y: pos.y }
}

const endSelection = () => {
  if (!isSelecting.value) return
  isSelecting.value = false

  const minX = Math.min(selectionStart.value.x, selectionEnd.value.x)
  const maxX = Math.max(selectionStart.value.x, selectionEnd.value.x)
  const minY = Math.min(selectionStart.value.y, selectionEnd.value.y)
  const maxY = Math.max(selectionStart.value.y, selectionEnd.value.y)

  objects.value.forEach(obj => {
    const objX = obj.position.x
    const objY = obj.position.y
    const objRight = objX + (obj.width || 100)
    const objBottom = objY + (obj.height || 100)

    if (objX >= minX && objX <= maxX && objY >= minY && objY <= maxY) {
      selectedObjects.value.add(obj.id)
    } else if (objRight >= minX && objRight <= maxX && objBottom >= minY && objBottom <= maxY) {
      selectedObjects.value.add(obj.id)
    }
  })

  selectionStart.value = { x: 0, y: 0 }
  selectionEnd.value = { x: 0, y: 0 }
}

const handleKeyDown = (event) => {
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return

  if (event.key === 'Escape') {
    selectedObjects.value.clear()
    isSelecting.value = false
  }

  if (event.key === 'Delete' || event.key === 'Backspace') {
    event.preventDefault()
    handleObjectDelete()
  }

  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'a') {
    event.preventDefault()
    objects.value.forEach(obj => selectedObjects.value.add(obj.id))
  }
}

const setTool = (tool) => {
  currentTool.value = tool
  if (tool !== 'addCard') {
    selectedCard.value = null
  }
}

defineExpose({
  zoomIn,
  zoomOut,
  resetZoom,
  setZoom,
  panOffset,
  zoom,
  isPanning,
  currentTool,
  setTool
})

onMounted(() => {
  nextTick(() => {
    initDrawCanvas()
  })
  window.addEventListener('mouseup', handleBoardMouseUp)
  window.addEventListener('mousemove', handleBoardMouseMove)
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('mouseup', handleBoardMouseUp)
  window.removeEventListener('mousemove', handleBoardMouseMove)
  window.removeEventListener('keydown', handleKeyDown)
})
</script>




<template>
  <div class="w-full h-full relative bg-slate-950 overflow-hidden" :style="{ cursor: cursorStyle }">
    <div ref="boardContainerRef" class="absolute inset-0 board-pan-area z-0" @click="handleBoardClick"
      @mousedown="handleBoardMouseDown">
      <div ref="boardRef" class="board-background" :style="gridStyles">
        <canvas ref="drawCanvasRef" class="draw-canvas absolute inset-0" style="z-index: 10; pointer-events: none;" />
        <div v-if="isSelecting" class="absolute border-2 border-violet-400 bg-violet-500/20 pointer-events-none" :style="{
          left: Math.min(selectionStart.x, selectionEnd.x) + 'px',
          top: Math.min(selectionStart.y, selectionEnd.y) + 'px',
          width: Math.abs(selectionEnd.x - selectionStart.x) + 'px',
          height: Math.abs(selectionEnd.y - selectionStart.y) + 'px',
          zIndex: 5
        }" />

        <GameObject v-for="obj in objects" :key="obj.id" :object="obj" :is-selected="selectedObjects.has(obj.id)"
          :is-draggable="currentTool === 'select'" :is-resizable="obj.resizable !== false" :zoom="zoom"
          :grid-size="gridSize" :snap-to-grid="false" @select="handleObjectSelect" @move="handleObjectMove"
          @delete="handleObjectDelete" @duplicate="handleObjectDuplicate" @rotate="handleObjectRotate" />
      </div>
    </div>
    <div
      class="absolute top-6 left-1/2 -translate-x-1/2 px-4 py-2 rounded-xl bg-slate-800/60 backdrop-blur border border-violet-500/30 text-sm text-violet-300 toolbar z-50">
      {{ currentTool === 'select' && `Select Tool — ${selectedObjects.size} selected — Ctrl+Click to multi-select` }}
      {{ currentTool === 'pan' && 'Pan Tool - Hold Alt + Drag' }}
      {{ currentTool === 'draw' && 'Draw Tool - Click and Drag' }}
      {{ currentTool === 'erase' && 'Erase Tool - Click and Drag' }}
      {{ currentTool === 'addCard' && 'Add Card Tool - Click on Board' }}
    </div>

    <div class="absolute left-6 top-1/2 -translate-y-1/2 flex flex-col gap-2 toolbar z-50">
      <button @click="setTool('select')" :class="[
        'w-12 h-12 rounded-xl flex items-center justify-center transition-all shadow-lg border',
        currentTool === 'select'
          ? 'bg-violet-600 text-white border-violet-400'
          : 'bg-slate-800/60 text-slate-300 hover:text-white border-white/10 hover:border-violet-500/50'
      ]" title="Select (V)">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
        </svg>
      </button>

      <button @click="setTool('pan')" :class="[
        'w-12 h-12 rounded-xl flex items-center justify-center transition-all shadow-lg border',
        currentTool === 'pan'
          ? 'bg-cyan-600 text-white border-cyan-400'
          : 'bg-slate-800/60 text-slate-300 hover:text-white border-white/10 hover:border-cyan-500/50'
      ]" title="Pan (Alt+Drag)">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11" />
        </svg>
      </button>

      <button @click="setTool('draw')" :class="[
        'w-12 h-12 rounded-xl flex items-center justify-center transition-all shadow-lg border',
        currentTool === 'draw'
          ? 'bg-amber-600 text-white border-amber-400'
          : 'bg-slate-800/60 text-slate-300 hover:text-white border-white/10 hover:border-amber-500/50'
      ]" title="Draw (P)">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
        </svg>
      </button>

      <button @click="setTool('erase')" :class="[
        'w-12 h-12 rounded-xl flex items-center justify-center transition-all shadow-lg border',
        currentTool === 'erase'
          ? 'bg-red-600 text-white border-red-400'
          : 'bg-slate-800/60 text-slate-300 hover:text-white border-white/10 hover:border-red-500/50'
      ]" title="Erase (E)">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>

      <button @click="showCardPanel = !showCardPanel" :class="[
        'w-12 h-12 rounded-xl flex items-center justify-center transition-all shadow-lg border',
        currentTool === 'addCard'
          ? 'bg-emerald-600 text-white border-emerald-400'
          : 'bg-slate-800/60 text-slate-300 hover:text-white border-white/10 hover:border-emerald-500/50'
      ]" title="Add Card (C)">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </div>

    <div v-if="showCardPanel"
      class="absolute left-24 top-1/2 -translate-y-1/2 w-64 bg-slate-800/90 backdrop-blur rounded-2xl border border-white/10 p-4 shadow-2xl z-50 toolbar">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-bold text-white">Select Card</h3>
        <button @click="showCardPanel = false" class="text-slate-400 hover:text-white">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="space-y-2">
        <button v-for="card in cardDeck" :key="card.id" @click="selectCardToAdd(card)"
          class="w-full p-3 rounded-xl bg-slate-700/50 hover:bg-slate-700 flex items-center gap-3 transition-all border border-white/5 hover:border-violet-500/50">
          <div
            class="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center text-white font-bold">
            {{ card.name[0] }}
          </div>
          <span class="font-medium text-slate-200">{{ card.name }}</span>
        </button>
      </div>

      <p class="text-xs text-slate-500 mt-3 text-center">Click on board to add</p>
    </div>

    <div v-if="currentTool === 'draw'"
      class="absolute left-24 top-6 w-48 bg-slate-800/90 backdrop-blur rounded-2xl border border-white/10 p-4 shadow-2xl z-50 toolbar">
      <h4 class="font-bold text-white mb-3">Brush Settings</h4>

      <div class="mb-3">
        <label class="text-xs text-slate-400 mb-2 block">Color</label>
        <div class="flex gap-2 flex-wrap">
          <button v-for="color in ['#8b5cf6', '#06b6d4', '#f43f5e', '#10b981', '#f59e0b', '#ffffff']" :key="color"
            @click="brushColor = color" :class="[
              'w-6 h-6 rounded-full border-2 transition-transform hover:scale-110',
              brushColor === color ? 'border-white scale-110' : 'border-transparent'
            ]" :style="{ background: color }" />
        </div>
      </div>

      <div>
        <label class="text-xs text-slate-400 mb-2 block">Size: {{ brushSize }}px</label>
        <input v-model="brushSize" type="range" min="1" max="20" class="w-full accent-violet-500" />
      </div>
    </div>

    <div class="absolute bottom-24 right-6 flex flex-col gap-2 toolbar z-50">
      <button @click="zoomIn()"
        class="w-12 h-12 rounded-xl bg-slate-800/60 hover:bg-slate-700 flex items-center justify-center text-white transition-all shadow-lg border border-white/10">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
        </svg>
      </button>
      <button @click="resetZoom()"
        class="w-12 h-12 rounded-xl bg-slate-800/60 hover:bg-slate-700 flex items-center justify-center text-white transition-all shadow-lg border border-white/10 text-xs font-bold">
        {{ Math.round(zoom * 100) }}%
      </button>
      <button @click="zoomOut()"
        class="w-12 h-12 rounded-xl bg-slate-800/60 hover:bg-slate-700 flex items-center justify-center text-white transition-all shadow-lg border border-white/10">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.board-background {
  background-color: #0f172a;
  will-change: transform;
  position: absolute;
  top: -50000px;
  left: -50000px;
  background-image:
    linear-gradient(rgba(139, 92, 246, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139, 92, 246, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  background-repeat: repeat;
}

.board-pan-area {
  touch-action: none;
  user-select: none;
}

.draw-canvas {
  touch-action: none;
}

.toolbar {
  pointer-events: auto;
}
</style>
