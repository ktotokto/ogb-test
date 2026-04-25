<script setup>
import { ref, computed, onMounted, watch, toRef } from 'vue'
import { useInteractDrag } from '@/composables/useInteractDrag'
import { X, RotateCw, Trash2, Copy, GripVertical, Maximize2, FlipVertical, Layers, Hand } from 'lucide-vue-next'
import { useGameWebSocket } from '@/composables/useGameWebSocket'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'

const { socket } = useGameWebSocket()
const gameStore = useGameStore()
const userStore = useUserStore()

const props = defineProps({
  object: { type: Object, required: true },
  isSelected: { type: Boolean, default: false },
  isDraggable: { type: Boolean, default: true },
  isResizable: { type: Boolean, default: true },
  zoom: { type: Number, default: 1 },
  gridSize: { type: Number, default: 20 },
  snapToGrid: { type: Boolean, default: false },
  isShiftPressed: {type: Boolean}
})

const emit = defineEmits([
  'select', 'move', 'resize', 'delete',
  'duplicate', 'rotate', 'drag-start', 'drag-end',
  'flip', 'stack-mode', 'stack-remove', 'add-object-to-hand'
])

const objectRef = ref(null)
const showContextMenu = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const isHovered = ref(false)
const isExpanded = computed(() => isHovered.value && props.isShiftPressed)

const { isDragging, position, updatePosition } = useInteractDrag(objectRef, {
  enabled: () => props.isDraggable,
  snapToGrid: props.snapToGrid,
  gridSize: props.gridSize,
  zoom: toRef(props, 'zoom'),

  onDragStart: (event, pos) => {
    emit('select', props.object)
    emit('drag-start', props.object)
  },

  onDragMove: (event, pos) => {
    emit('move', {
      objectId: props.object.id,
      position: { x: pos.x, y: pos.y },
      live: true
    })

    if (socket?.value && gameStore.sessionId) {
      console.log('📤 Emitting object:sync (move):', {
        sessionId: gameStore.sessionId,
        userId: userStore.userId,
        objectId: props.object.id,
        position: { x: pos.x, y: pos.y }
      })

      socket.value.emit('object:sync', {
        sessionId: gameStore.sessionId,
        userId: userStore.userId,
        update: {
          objectId: props.object.id,
          changes: { position: { x: pos.x, y: pos.y } },
          type: 'move'
        }
      })
    }
  },

  onDragEnd: (event, pos) => {
    const finalX = props.snapToGrid ? Math.round(pos.x / props.gridSize) * props.gridSize : pos.x
    const finalY = props.snapToGrid ? Math.round(pos.y / props.gridSize) * props.gridSize : pos.y

    emit('move', {
      objectId: props.object.id,
      position: { x: finalX, y: finalY },
      final: true
    })

    if (socket?.value && gameStore.sessionId) {
      console.log('📤 Emitting object:sync (end):', {
        sessionId: gameStore.sessionId,
        userId: userStore.userId,
        objectId: props.object.id,
        position: { x: finalX, y: finalY }
      })

      socket.value.emit('object:sync', {
        sessionId: gameStore.sessionId,
        userId: userStore.userId,
        update: {
          objectId: props.object.id,
          changes: { position: { x: finalX, y: finalY } },
          type: 'move-end'
        }
      })
    }

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
  zIndex: isExpanded.value ? 1000 : (props.object.stackId ? (props.object.stackIndex + 1) * 10 : (props.object.zIndex || 1)),
  // transform: isExpanded.value ? 'scale(1.5)' : `rotate(${props.object.rotation}deg)`,
  // transition: isExpanded.value ? 'transform 0.2s ease-out, z-index 0s' : 'transform 0.3s ease-in-out'
}))

const getObjectIcon = (type) => {
  const icons = { card: '🎴', dice: '🎲', token: '🔵', model: '🎭', image: '🖼️', text: '📝' }
  return icons[type] || '📦'
}

const handleClick = (event) => {
  if (isDragging.value) return
  event.stopPropagation()
  emit('select', props.object, event)
}

const handleContextMenu = (event) => {
  event.preventDefault()
  event.stopPropagation()
  contextMenuPosition.value = { x: event.clientX, y: event.clientY }
  showContextMenu.value = true
  emit('select', props.object)
}

const handleDelete = () => {
  emit('delete', props.object.id)

  if (socket?.value && gameStore.sessionId) {
    socket.value.emit('object:delete', {
      sessionId: gameStore.sessionId,
      objectId: props.object.id
    })
  }

  showContextMenu.value = false
}

const handleAddHand = () => {
  emit('add-object-to-hand', props.object)
  emit('delete', props.object.id)
}

const handleDuplicate = () => {
  const newObject = {
    ...props.object,
    id: `obj_${Date.now()}`,
    position: {
      x: props.object.position.x + 20,
      y: props.object.position.y + 20
    }
  }
  emit('duplicate', newObject)

  if (socket?.value && gameStore.sessionId) {
    socket.value.emit('object:create', {
      sessionId: gameStore.sessionId,
      object: newObject
    })
  }

  showContextMenu.value = false
}

const handleRotate = () => {
  const newRotation = ((props.object.rotation || 0) + 90) % 360
  emit('rotate', { objectId: props.object.id, rotation: newRotation })

  if (socket?.value && gameStore.sessionId) {
    socket.value.emit('object:sync', {
      sessionId: gameStore.sessionId,
      userId: userStore.userId,
      update: {
        objectId: props.object.id,
        changes: { rotation: newRotation },
        type: 'rotate'
      }
    })
  }
}

const handleFlip = () => {
  emit('flip', props.object.id)

  if (socket?.value && gameStore.sessionId) {
    socket.value.emit('object:sync', {
      sessionId: gameStore.sessionId,
      userId: userStore.userId,
      update: {
        objectId: props.object.id,
        changes: { faceUp: !props.object.faceUp },
        type: 'flip'
      }
    })
  }

  showContextMenu.value = false
}

const closeContextMenu = () => {
  showContextMenu.value = false
}

const stackCount = computed(() => {
  if (!props.object.stackId) return 0
  return props.object._stackCount || 0
})

const isTopOfStack = computed(() => {
  if (!props.object.stackId) return false
  return props.object.stackIndex === Math.max(0, stackCount.value - 1)
})
</script>

<template>
  <div ref="objectRef" class="absolute select-none game-object group" :style="objectStyles" @click="handleClick"
    @contextmenu="handleContextMenu" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
    <div class="w-full h-full rounded-2xl transition-all duration-300 relative" :class="[
      isSelected
        ? 'ring-2 ring-violet-400 shadow-[0_0_40px_rgba(139,92,246,0.5)] scale-105'
        : 'hover:shadow-[0_0_30px_rgba(139,92,246,0.3)]',
      isDragging ? 'cursor-grabbing z-50' : 'cursor-grab',
      isHovered && !isSelected && 'ring-1 ring-violet-500/50'
    ]" :style="{
      backdropFilter: 'blur(12px)',
      border: isSelected ? '2px solid rgba(139,92,246,0.8)' : '1px solid rgba(255,255,255,0.1)',
      rotate: `${props.object.rotation}deg`,
      transition: object.faceUp === false ? 'transform 0.3s' : 'none',
      transformStyle: 'preserve-3d'
    }">
      <template v-if="object.stackId && !isTopOfStack">
        <div class="absolute inset-0 rounded-2xl bg-slate-700/50" :style="{
          transform: `translate(${-(stackCount - stackIndex - 1) * 2}px, ${-(stackCount - stackIndex - 1) * 2}px)`
        }"></div>
      </template>

      <div
        class="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
      </div>

      <div v-if="isSelected && !isDragging"
        class="absolute -top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 z-10">
        <div class="px-3 py-1 rounded-full glass bg-violet-500/20 border border-violet-500/50 text-xs text-violet-300">
          {{ object.label || object.type }}
        </div>
      </div>

      <!-- Stack badge -->
      <div v-if="stackCount > 1"
        class="absolute -top-2 -right-2 z-20 w-6 h-6 rounded-full bg-violet-600 text-white text-xs font-bold flex items-center justify-center shadow-lg">
        {{ stackCount }}
      </div>

      <!-- Card content -->
      <div class="w-full h-full flex items-center justify-center relative">
        <!-- Card type: render with flip -->
        <template v-if="object.type === 'card'">
          <!-- Face up -->
          <div v-if="object.faceUp !== false" class="w-full h-full flex flex-col items-center justify-center p-2">
            <template v-if="object.cardData?.frontImage">
              <img :src="object.cardData.frontImage" class="w-full h-full object-cover rounded-xl" draggable="false" />
            </template>
            <template v-else>
              <div class="text-3xl filter drop-shadow-lg">🎴</div>
              <div v-if="object.label" class="absolute bottom-2 left-0 right-0 text-center">
                <span class="text-xs font-medium px-2 py-1 rounded-full glass text-slate-300">
                  {{ object.label }}
                </span>
              </div>
            </template>
          </div>
          <!-- Face down (card back) -->
          <div v-else
            class="w-full h-full flex items-center justify-center rounded-xl">
            <div v-if="object.cardData?.backImage">
              <img :src="object.cardData.backImage" class="w-full h-full object-cover rounded-xl" draggable="false" />
            </div>
            <div v-else class="text-5xl opacity-50">🎴</div>
          </div>
        </template>

        <!-- Image type -->
        <template v-else-if="object.type === 'image' && object.url">
          <img :src="object.url" class="w-full h-full object-contain rounded-lg" draggable="false" />
        </template>

        <!-- Default: icon + label -->
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

      <template v-if="isSelected">
        <div
          class="absolute -top-1.5 -left-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_10px_rgba(139,92,246,0.8)]">
        </div>
        <div
          class="absolute -top-1.5 -right-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_10px_rgba(139,92,246,0.8)]">
        </div>
        <div
          class="absolute -bottom-1.5 -left-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_10px_rgba(139,92,246,0.8)]">
        </div>
        <div
          class="absolute -bottom-1.5 -right-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_10px_rgba(139,92,246,0.8)]">
        </div>
      </template>
      <div
        class="absolute -top-12 left-1/2 -translate-x-1/2 flex gap-1 glass-strong rounded-xl p-1.5 shadow-2xl opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0 z-30">
        <button v-if="object.type === 'card'" @click.stop="handleFlip"
          class="p-2 rounded-lg hover:bg-amber-500/20 text-slate-300 hover:text-amber-300 transition-colors"
          :title="object.faceUp === false ? 'Повернуть лицом вверх' : 'Повернуть лицом вниз'">
          <FlipVertical class="w-4 h-4" />
        </button>
        <button v-if="object.type === 'card'" @click.stop="emit('stack-mode', object.id)"
          class="p-2 rounded-lg hover:bg-emerald-500/20 text-slate-300 hover:text-emerald-300 transition-colors"
          title="Добавить в стопку">
          <Layers class="w-4 h-4" />
        </button>
        <button @click.stop="handleRotate"
          class="p-2 rounded-lg hover:bg-violet-500/20 text-slate-300 hover:text-violet-300 transition-colors"
          title="Повернуть">
          <RotateCw class="w-4 h-4" />
        </button>
        <button @click.stop="handleDuplicate"
          class="p-2 rounded-lg hover:bg-cyan-500/20 text-slate-300 hover:text-cyan-300 transition-colors"
          title="Копировать">
          <Copy class="w-4 h-4" />
        </button>
        <button @click.stop="handleAddHand"
          class="p-2 rounded-lg hover:bg-red-500/20 text-slate-300 hover:text-orange-400 transition-colors"
          title="Взять в руку">
          <Hand class="w-4 h-4" />
        </button>
        <button @click.stop="handleDelete"
          class="p-2 rounded-lg hover:bg-red-500/20 text-slate-300 hover:text-red-400 transition-colors"
          title="Удалить">
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showContextMenu"
        class="fixed glass-strong rounded-2xl shadow-2xl py-2 z-[100] min-w-[200px] border border-white/10 animate-slide-in"
        :style="{ left: `${contextMenuPosition.x}px`, top: `${contextMenuPosition.y}px` }" @click.stop>
        <div class="px-4 py-2 text-xs font-semibold text-slate-400 border-b border-white/10 mb-1">
          {{ object.label || object.type }}
        </div>
        <button @click="handleDuplicate"
          class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-violet-500/10 hover:text-violet-300 flex items-center gap-3 transition-colors">
          <Copy class="w-4 h-4" /> Копировать
        </button>
        <button v-if="object.type === 'card'" @click="handleFlip"
          class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-amber-500/10 hover:text-amber-300 flex items-center gap-3 transition-colors">
          <FlipVertical class="w-4 h-4" /> {{ object.faceUp === false ? 'Лицом вверх' : 'Лицом вниз' }}
        </button>
        <button v-if="object.stackId" @click="emit('stack-remove', object.id); showContextMenu.value = false"
          class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-orange-500/10 hover:text-orange-300 flex items-center gap-3 transition-colors">
          <Layers class="w-4 h-4" /> Убрать из стопки
        </button>
        <button @click="handleRotate"
          class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-cyan-500/10 hover:text-cyan-300 flex items-center gap-3 transition-colors">
          <RotateCw class="w-4 h-4" /> Повернуть на 90°
        </button>
        <hr class="border-white/10 my-1" />
        <button @click="handleDelete"
          class="w-full px-4 py-2.5 text-left text-sm text-red-400 hover:bg-red-500/10 flex items-center gap-3 transition-colors">
          <Trash2 class="w-4 h-4" /> Удалить
        </button>
        <button @click="closeContextMenu"
          class="w-full px-4 py-2 text-left text-xs text-slate-500 hover:text-slate-400 mt-1">
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