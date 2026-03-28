<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useInteractDrag } from '@/composables/useInteractDrag'
import { X, RotateCw, Trash2, Copy, GripVertical, Maximize2 } from 'lucide-vue-next'

const props = defineProps({
  object: { type: Object, required: true },
  isSelected: { type: Boolean, default: false },
  isDraggable: { type: Boolean, default: true },
  isResizable: { type: Boolean, default: true },
  zoom: { type: Number, default: 1 },
  gridSize: { type: Number, default: 20 },
  snapToGrid: { type: Boolean, default: false }
})

const emit = defineEmits(['select', 'move', 'resize', 'delete', 'duplicate', 'rotate', 'drag-start', 'drag-end'])

const objectRef = ref(null)
const showContextMenu = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const isHovered = ref(false)

const { isDragging, position, updatePosition } = useInteractDrag(objectRef, {
  enabled: props.isDraggable,
  snapToGrid: props.snapToGrid,
  gridSize: props.gridSize,
  onDragStart: (event, pos) => {
    emit('select', props.object)
    emit('drag-start', props.object)
  },
  onDragMove: (event, pos) => {
    emit('move', { objectId: props.object.id, position: { x: pos.x, y: pos.y }, live: true })
  },
  onDragEnd: (event, pos) => {
    const finalX = props.snapToGrid ? Math.round(pos.x / props.gridSize) * props.gridSize : pos.x
    const finalY = props.snapToGrid ? Math.round(pos.y / props.gridSize) * props.gridSize : pos.y
    emit('move', { objectId: props.object.id, position: { x: finalX, y: finalY }, final: true })
    emit('drag-end', props.object)
  }
})

onMounted(() => {
  if (props.object.position && objectRef.value) {
    updatePosition(props.object.position.x, props.object.position.y)
  }
})

watch(() => props.object.position, (newPos) => {
  if (newPos && !isDragging.value) {
    updatePosition(newPos.x, newPos.y)
  }
}, { deep: true })

const objectStyles = computed(() => ({
  width: `${props.object.width || 100}px`,
  height: `${props.object.height || 100}px`,
  zIndex: props.object.zIndex || 1
}))

const getObjectIcon = (type) => {
  const icons = { card: 'Карта', dice: 'Кубик', token: 'Токен', model: 'Модель', image: 'Картинка', text: 'Текст' }
  return icons[type] || '📦'
}

const handleClick = (event) => {
  if (isDragging.value) return
  event.stopPropagation()
  emit('select', props.object)
}

const handleContextMenu = (event) => {
  event.preventDefault()
  event.stopPropagation()
  contextMenuPosition.value = { x: event.clientX, y: event.clientY }
  showContextMenu.value = true
  emit('select', props.object)
}

const handleDelete = () => { emit('delete', props.object.id); showContextMenu.value = false }
const handleDuplicate = () => {
  emit('duplicate', { ...props.object, id: `obj_${Date.now()}`, position: { x: props.object.position.x + 20, y: props.object.position.y + 20 } })
  showContextMenu.value = false
}
const handleRotate = () => {
  emit('rotate', { objectId: props.object.id, rotation: ((props.object.rotation || 0) + 90) % 360 })
}
const closeContextMenu = () => { showContextMenu.value = false }
</script>

<template>
  <div
    ref="objectRef"
    class="absolute select-none game-object group"
    :style="objectStyles"
    @click="handleClick"
    @contextmenu="handleContextMenu"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <div
      class="w-full h-full rounded-2xl transition-all duration-300 relative overflow-hidden"
      :class="[
        isSelected 
          ? 'ring-2 ring-violet-400 shadow-[0_0_40px_rgba(139,92,246,0.5)] scale-105' 
          : 'hover:shadow-[0_0_30px_rgba(139,92,246,0.3)]',
        isDragging ? 'cursor-grabbing z-50' : 'cursor-grab',
        isHovered && !isSelected && 'ring-1 ring-violet-500/50'
      ]"
      :style="{
        background: isSelected 
          ? 'linear-gradient(135deg, rgba(139,92,246,0.3), rgba(6,182,212,0.3))' 
          : 'linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9))',
        backdropFilter: 'blur(12px)',
        border: isSelected ? '2px solid rgba(139,92,246,0.8)' : '1px solid rgba(255,255,255,0.1)'
      }"
    >
      <!-- Shine effect -->
      <div class="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
      
      <!-- Drag handle -->
      <div v-if="isSelected && !isDragging" class="absolute -top-4 left-1/2 -translate-x-1/2 flex items-center gap-2">
        <div class="px-3 py-1 rounded-full glass bg-violet-500/20 border border-violet-500/50 text-xs text-violet-300">
          {{ object.label || object.type }}
        </div>
      </div>

      <!-- Content -->
      <div class="w-full h-full flex items-center justify-center p-3 relative">
        <template v-if="object.type === 'image' && object.url">
          <img :src="object.url" class="w-full h-full object-contain rounded-lg" draggable="false" />
        </template>
        <template v-else>
          <div class="text-5xl filter drop-shadow-lg transform group-hover:scale-110 transition-transform duration-300">
            {{ getObjectIcon(object.type) }}
          </div>
          <div v-if="object.label" class="absolute bottom-2 left-0 right-0 text-center">
            <span class="text-xs font-medium px-2 py-1 rounded-full glass text-slate-300">
              {{ object.label }}
            </span>
          </div>
        </template>
      </div>

      <!-- Selection indicators -->
      <template v-if="isSelected">
        <div class="absolute -top-1.5 -left-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_10px_rgba(139,92,246,0.8)]"></div>
        <div class="absolute -top-1.5 -right-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_10px_rgba(139,92,246,0.8)]"></div>
        <div class="absolute -bottom-1.5 -left-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_10px_rgba(139,92,246,0.8)]"></div>
        <div class="absolute -bottom-1.5 -right-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_10px_rgba(139,92,246,0.8)]"></div>
      </template>

      <!-- Quick actions -->
      <div v-if="isSelected && !isDragging" class="absolute -top-12 left-1/2 -translate-x-1/2 flex gap-1 glass-strong rounded-xl p-1.5 shadow-2xl opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
        <button @click.stop="handleRotate" class="p-2 rounded-lg hover:bg-violet-500/20 text-slate-300 hover:text-violet-300 transition-colors" title="Повернуть">
          <RotateCw class="w-4 h-4" />
        </button>
        <button @click.stop="handleDuplicate" class="p-2 rounded-lg hover:bg-cyan-500/20 text-slate-300 hover:text-cyan-300 transition-colors" title="Копировать">
          <Copy class="w-4 h-4" />
        </button>
        <button @click.stop="handleDelete" class="p-2 rounded-lg hover:bg-red-500/20 text-slate-300 hover:text-red-400 transition-colors" title="Удалить">
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Context Menu -->
    <Teleport to="body">
      <div v-if="showContextMenu" class="fixed glass-strong rounded-2xl shadow-2xl py-2 z-[100] min-w-[200px] border border-white/10 animate-slide-in" :style="{ left: `${contextMenuPosition.x}px`, top: `${contextMenuPosition.y}px` }" @click.stop>
        <div class="px-4 py-2 text-xs font-semibold text-slate-400 border-b border-white/10 mb-1">
          {{ object.label || object.type }}
        </div>
        <button @click="handleDuplicate" class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-violet-500/10 hover:text-violet-300 flex items-center gap-3 transition-colors">
          <Copy class="w-4 h-4" /> Копировать
        </button>
        <button @click="handleRotate" class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-cyan-500/10 hover:text-cyan-300 flex items-center gap-3 transition-colors">
          <RotateCw class="w-4 h-4" /> Повернуть на 90°
        </button>
        <hr class="border-white/10 my-1" />
        <button @click="handleDelete" class="w-full px-4 py-2.5 text-left text-sm text-red-400 hover:bg-red-500/10 flex items-center gap-3 transition-colors">
          <Trash2 class="w-4 h-4" /> Удалить
        </button>
        <button @click="closeContextMenu" class="w-full px-4 py-2 text-left text-xs text-slate-500 hover:text-slate-400 mt-1">
          Закрыть
        </button>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.game-object {
  will-change: transform;
}
</style>