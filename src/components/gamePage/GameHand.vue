<script setup>
import { ref, onUnmounted, watch } from 'vue'

const isDisplay = ref(true)
const hoveredCardId = ref(null)
const handHeight = ref(250)
const handWidth = ref(500)
const isResizingHeight = ref(false)
const isResizingWidth = ref(false)
const resizeStartY = ref(0)
const resizeStartHeight = ref(0)
const resizeStartX = ref(0)
const resizeStartWidth = ref(0)

const panOffset = ref({ x: 0, y: 0 })
const lastMousePos = ref({ x: 0, y: 0 })

const props = defineProps({
  objects: Array,
  isShiftPressed: { type: Boolean, default: false }
})

const emit = defineEmits(['remove-card', 'select-card'])

const toggleHand = () => {
  isDisplay.value = !isDisplay.value
}

const returnToBoard = (object) => {
  emit('select-card', object)
  const index = props.objects.indexOf(object)
  if (index !== -1) { props.objects.splice(index, 1) }
}

const startResizeHeight = (e) => {
  e.preventDefault()
  e.stopPropagation()
  isResizingHeight.value = true
  resizeStartY.value = e.clientY
  resizeStartHeight.value = handHeight.value
  window.addEventListener('mousemove', onResizeHeight)
  window.addEventListener('mouseup', stopResizeHeight)
}

const onResizeHeight = (e) => {
  if (!isResizingHeight.value) return
  const delta = resizeStartY.value - e.clientY
  handHeight.value = Math.max(150, Math.min(400, resizeStartHeight.value + delta))
}

const stopResizeHeight = () => {
  isResizingHeight.value = false
  window.removeEventListener('mousemove', onResizeHeight)
  window.removeEventListener('mouseup', stopResizeHeight)
}

const startResizeWidth = (e) => {
  e.preventDefault()
  e.stopPropagation()
  isResizingWidth.value = true
  resizeStartX.value = e.clientX
  resizeStartWidth.value = handWidth.value
  window.addEventListener('mousemove', onResizeWidth)
  window.addEventListener('mouseup', stopResizeWidth)
}

const onResizeWidth = (e) => {
  if (!isResizingWidth.value) return
  const delta = e.clientX - resizeStartX.value
  handWidth.value = Math.max(400, Math.min(window.innerWidth * 0.95, resizeStartWidth.value + delta))
}

const stopResizeWidth = () => {
  isResizingWidth.value = false
  window.removeEventListener('mousemove', onResizeWidth)
  window.removeEventListener('mouseup', stopResizeWidth)
}

const handleCardEnter = (id, e) => {
  hoveredCardId.value = id
  lastMousePos.value = { x: e.clientX, y: e.clientY }
  panOffset.value = { x: 0, y: 0 }
}

const handleCardMove = (id, e) => {
  if (!props.isShiftPressed || hoveredCardId.value !== id) return
  panOffset.value.x -= e.clientX - lastMousePos.value.x
  panOffset.value.y -= e.clientY - lastMousePos.value.y
  lastMousePos.value = { x: e.clientX, y: e.clientY }
}

const handleCardLeave = () => {
  hoveredCardId.value = null
  panOffset.value = { x: 0, y: 0 }
}

const getCardTransform = (id) => {
  if (!props.isShiftPressed || hoveredCardId.value !== id) return 'scale(1)'
  return `scale(3) translateY(-15%) translate(${panOffset.value.x}px, ${panOffset.value.y}px)`
}

watch(() => props.isShiftPressed, (val) => {
  if (!val) {
    panOffset.value = { x: 0, y: 0 }
    hoveredCardId.value = null
  }
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onResizeHeight)
  window.removeEventListener('mouseup', stopResizeHeight)
  window.removeEventListener('mousemove', onResizeWidth)
  window.removeEventListener('mouseup', stopResizeWidth)
})
</script>

<template>
  <div class="hand-container" :style="{ width: `${handWidth}px` }">
    <div v-if="isDisplay" class="resize-handle-top" @mousedown="startResizeHeight">
      <div class="resize-grip-h"></div>
    </div>
    <div v-if="isDisplay" class="resize-handle-right" @mousedown="startResizeWidth">
      <div class="resize-grip-v"></div>
    </div>
    
    <div class="hand-header">
      <div class="flex items-center gap-2">
        <span class="hand-title">Рука</span>
        <span class="hand-count">{{ objects.length }}</span>
      </div>
    </div>

    <div v-if="isDisplay" class="hand-main-section">
      <div v-if="!objects || objects.length === 0" class="hand-empty">
        <span class="hand-empty-text">Рука пуста</span>
      </div>
      <div v-else class="hand-cards-wrapper" :style="{ height: `${handHeight}px` }">
        <div class="hand-cards">
          <div 
            v-for="object in objects" 
            :key="object.id" 
            class="hand-card"
            :class="{ 'is-hovered': hoveredCardId === object.id && isShiftPressed }"
            :style="{ transform: getCardTransform(object.id) }"
            @mouseenter="handleCardEnter(object.id, $event)" 
            @mousemove="handleCardMove(object.id, $event)" 
            @mouseleave="handleCardLeave" 
            @click="returnToBoard(object)"
          >
            <div class="hand-card-inner">
              <template v-if="object.cardData?.frontImage">
                <img :src="object.cardData.frontImage" class="hand-card-image-full" draggable="false" />
              </template>
              <template v-else>
                <div class="hand-card-label-overlay">
                  <span class="hand-card-label">{{ object.label || 'Карта' }}</span>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="hand-footer">
      <button @click="toggleHand" class="footer-text">Скрыть руку</button>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.hand-container {
  @apply absolute bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3 max-w-[95vw] w-auto;
  z-index: 40;
  transition: width 0.1s ease-out;
}

.resize-handle-top {
  @apply absolute -top-4 left-6 right-6 h-8 cursor-ns-resize flex items-center justify-center z-50;
}

.resize-handle-right {
  @apply absolute top-8 bottom-8 -right-4 w-8 cursor-ew-resize flex items-center justify-center z-50;
}

.resize-grip-h {
  @apply w-16 h-1.5 rounded-full bg-slate-600/50 hover:bg-violet-500/70 transition-colors;
}

.resize-grip-v {
  @apply w-1.5 h-16 rounded-full bg-slate-600/50 hover:bg-violet-500/70 transition-colors;
}

.hand-header {
  @apply flex items-center justify-center w-full px-2 pointer-events-none;
}

.hand-title {
  @apply text-sm font-bold text-slate-300 uppercase tracking-wider;
}

.hand-count {
  @apply px-2 py-0.5 rounded-full bg-violet-600/30 border border-violet-500/30 text-violet-300 text-xs font-mono;
}

.hand-main-section {
  @apply w-full;
}

.hand-cards-wrapper {
  @apply rounded-2xl bg-slate-800/50 backdrop-blur-md border border-white/10 shadow-2xl overflow-y-auto relative;
  transition: height 0.2s ease;
  overflow-x: visible;
}

.hand-cards {
  @apply flex flex-wrap justify-center gap-4 px-8 pb-4 scroll-smooth absolute inset-0 overflow-y-auto;
  padding-top: 40px;
}

.hand-card {
  @apply relative w-32 h-44 rounded-xl cursor-pointer select-none flex-shrink-0 transition-all duration-200;
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  will-change: transform;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.hand-card:hover {
  @apply border-violet-500/40;
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
}

.hand-card.is-hovered {
  z-index: 100 !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
  border-color: rgba(139, 92, 246, 0.8) !important;
}

.hand-card-inner {
  @apply w-full h-full relative rounded-xl overflow-hidden pointer-events-none;
}

.hand-card-image-full {
  @apply absolute inset-0 w-full h-full object-cover;
  image-rendering: -webkit-optimize-contrast;
}

.hand-card-placeholder {
  @apply absolute inset-0 flex items-center justify-center text-5xl opacity-50;
}

.hand-card-label-overlay {
  @apply absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent pointer-events-none;
}

.hand-card-label {
  @apply text-xs font-semibold text-white text-center line-clamp-2 block drop-shadow-md;
}

.hand-footer {
  @apply mt-1;
}

.footer-text {
  @apply px-4 py-1.5 rounded-full bg-slate-700/40 hover:bg-slate-700/60 border border-white/5 text-slate-400 hover:text-white text-xs transition-all duration-200 cursor-pointer;
}

.hand-cards::-webkit-scrollbar {
  @apply w-1.5;
}

.hand-cards::-webkit-scrollbar-thumb {
  @apply rounded-full bg-violet-600/40 hover:bg-violet-600/60;
}

.hand-empty {
  @apply px-10 py-8 rounded-2xl bg-slate-800/50 backdrop-blur-md border border-white/10;
}

.hand-empty-text {
  @apply text-slate-500 text-sm italic;
}
</style>