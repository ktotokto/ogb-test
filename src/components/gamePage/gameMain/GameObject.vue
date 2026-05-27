<script setup>
import { ref, computed, onMounted, watch, toRef } from 'vue'
import { useInteractDrag } from '@/composables/useInteractDrag'
import { RotateCcw, Trash2, Copy, FlipVertical, Layers, Hand, Plus, Shuffle, LayoutGrid, Lock, Box } from 'lucide-vue-next'
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
  isShiftPressed: { type: Boolean }
})

const emit = defineEmits([
  'select', 'move', 'resize', 'delete',
  'duplicate', 'rotate', 'drag-start', 'drag-end',
  'flip', 'stack-remove', 'add-object-to-hand',
  'draw-from-deck', 'shuffle-deck', 'spread-deck'
])

const objectRef = ref(null)
const showContextMenu = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const isHovered = ref(false)
const isExpanded = computed(() => isHovered.value && props.isShiftPressed)
const isDeck = computed(() => props.object.type === 'deck')
const deckCardCount = computed(() => props.object.cardCount || props.object.cards?.length || 0)
const isDragEnabled = computed(() => props.isDraggable && !props.object.locked)

const { isDragging, position, updatePosition } = useInteractDrag(objectRef, {
  enabled: isDragEnabled,
  snapToGrid: props.snapToGrid,
  gridSize: props.gridSize,
  zoom: toRef(props, 'zoom'),

  onDragStart: (event, pos) => {
    if (props.object.locked) return false
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

const toggleObjectLock = () => {
  props.object.locked = !props.object.locked

  gameStore.updateObject(props.object.id, { locked: props.object.locked })
  gameStore.debouncedSave()
  if (socket?.value && gameStore.sessionId) {
    socket.value.emit('object:sync', {
      sessionId: gameStore.sessionId,
      userId: userStore.userId,
      update: {
        objectId: props.object.id,
        changes: { locked: !props.object.locked },
        type: 'object-lock'
      }
    })
  }

  showContextMenu.value = false
}
const handleDrawFromDeck = () => {
  if (!isDeck.value) return
  emit('draw-from-deck', props.object.id, props.object.position)
}

const handleShuffleDeck = () => {
  if (!isDeck.value) return
  emit('shuffle-deck', props.object.id)
}

const handleSpreadDeck = () => {
  if (!isDeck.value) return
  emit('spread-deck', props.object.id, props.object.position)
}

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
  transformOrigin: 'center center'
}))

const rotateStyle = computed(() => ({
  rotate: `-${props.object.rotation}deg`,
  transformOrigin: 'center center'
}))

const handleClick = (event) => {
  if (isDragging.value || isExpanded.value) return
  event.stopPropagation()
  emit('select', props.object, event)
}

const handleContextMenu = (event) => {
  if (isDeck.value && deckCardCount.value > 0) {
    console.log(props.object);
    
    event.preventDefault()
    emit('draw-from-deck', props.object.id, props.object.position)
    return
  }

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
  if (isDeck.value) {
    gameStore.removeDeck(props.object.id)
  }
  showContextMenu.value = false
}

const handleAddHand = () => {
  emit('add-to-hand', props.object.id)
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
  emit('rotate', { 
    objectId: props.object.id, 
    rotation: newRotation 
  })
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
    @contextmenu.prevent="handleContextMenu" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
    <div class="w-full h-full relative transition-all duration-300 ease-out" :style="rotateStyle" :class="[
      isDragging ? 'cursor-grabbing z-50 scale-105' : 'cursor-grab hover:scale-[1.02]',
      object.locked ? 'cursor-not-allowed opacity-80' : '',
      isHovered && !isSelected && 'ring-2 ring-violet-400/30 shadow-[0_0_20px_rgba(139,92,246,0.2)]',
    ]">

      <template v-if="object.stackId && !isTopOfStack">
        <div class="absolute inset-0 bg-slate-700/50"
          :style="{ transform: `translate(${-(stackCount - stackIndex - 1) * 2}px, ${-(stackCount - stackIndex - 1) * 2}px)` }">
        </div>
      </template>

      <div
        class="absolute inset-0 bg-gradient-to-br from-white/15 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
      </div>

      <div v-if="isSelected && !isDragging && object.faceUp !== false"
        class="absolute -top-5 left-1/2 -translate-x-1/2 z-20 pointer-events-none">
        <div
          class="px-3 py-1 rounded-full bg-slate-900/80 backdrop-blur-md border border-violet-500/40 shadow-lg text-[10px] font-semibold text-violet-200 tracking-wide uppercase">
          {{ object.label || object.type }}
        </div>
      </div>

      <div v-if="stackCount > 1"
        class="absolute -top-2.5 -right-2.5 z-20 w-7 h-7 rounded-full bg-violet-600 text-white text-xs font-bold flex items-center justify-center shadow-lg border-2 border-slate-900">
        {{ stackCount }}
      </div>

      <div class="w-full h-full relative overflow-hidden transition-all duration-300" :class="[
        object.shape === 'circle' ? 'rounded-full' : object.shape === 'rounded' ? 'rounded-2xl' : 'rounded-xl',
        isSelected ? 'ring-2 ring-violet-400 shadow-[0_0_30px_rgba(139,92,246,0.4)]' : 'hover:ring-1 hover:ring-white/20',
        object.locked ? 'border-2 border-amber-500/60' : 'border border-white/10',
        object.type === 'deck' ? 'bg-gradient-to-br from-violet-950 to-slate-900' : '',
        object.type === 'card' ? 'bg-slate-800/60' : '',
        object.type === 'character' ? (object.isEnemy ? 'bg-gradient-to-br from-red-950/90 to-slate-900' : 'bg-gradient-to-br from-emerald-950/90 to-slate-900') : '',
        (object.type === 'model2d' || object.type === 'image') ? 'bg-slate-800/40' : ''
      ]">

        <template v-if="isDeck">
          <div class="w-full h-full flex flex-col items-center justify-center p-3">
            <div class="text-white font-bold text-2xl drop-shadow-md">{{ deckCardCount }}</div>
            <div class="text-slate-400 text-[10px] font-medium uppercase tracking-wider mt-1">карт</div>
            <div class="text-slate-300 text-[10px] mt-2 text-center px-2 line-clamp-2 max-w-[90%] font-medium">
              {{ object.label || 'Колода' }}
            </div>
          </div>
          <div v-if="deckCardCount === 0"
            class="absolute inset-0 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm pointer-events-none">
            <div class="text-slate-400 text-[10px] font-medium">Пусто</div>
          </div>
        </template>

        <template v-else-if="object.type === 'card'">
          <div v-if="object.faceUp !== false" class="w-full h-full flex flex-col items-center justify-center p-2">
            <template v-if="object.cardData?.frontImage">
              <img :src="object.cardData.frontImage" class="w-full h-full object-cover" draggable="false" />
            </template>
            <template v-else>
              <div v-if="object.label && !object.cardData?.frontImage"
                class="absolute bottom-2 left-0 right-0 text-center">
                <span
                  class="text-[10px] font-medium px-2 py-1 rounded-full bg-black/40 text-slate-200 backdrop-blur-sm border border-white/10">{{
                  object.label }}</span>
              </div>
            </template>
          </div>
          <div v-else class="w-full h-full flex items-center justify-center">
            <template v-if="object.cardData?.backImage">
              <img :src="object.cardData.backImage" class="w-full h-full object-cover" draggable="false" />
            </template>
          </div>
        </template>

        <template v-else-if="object.type === 'model2d' || object.type === 'image'">
          <template v-if="object.url">
            <img :src="object.url" class="w-full h-full object-cover"
              :class="object.shape === 'circle' ? 'object-center' : 'object-contain'" draggable="false" />
          </template>
          <template v-else>
            <div class="w-full h-full flex flex-col items-center justify-center text-slate-400">
              <Box class="w-8 h-8 mb-2 opacity-50" />
              <span class="text-[10px] font-medium">Нет изображения</span>
            </div>
          </template>
          <div v-if="object.label && !object.url && object.faceUp !== false"
            class="absolute bottom-0 left-0 right-0 px-2 py-1.5 bg-gradient-to-t from-black/80 to-transparent text-center">
            <span class="text-[10px] text-slate-200 font-medium truncate block">{{ object.label }}</span>
          </div>
        </template>

        <template v-else-if="object.type === 'character'">
          <div v-if="object.characterImage" class="w-full h-full relative">
            <img :src="object.characterImage" class="w-full h-full object-cover"
              :class="object.shape === 'circle' ? 'object-center' : 'object-contain'" draggable="false" />
            <div v-if="object.isEnemy" class="absolute inset-0 bg-red-900/20 pointer-events-none"></div>
          </div>

          <div class="absolute bottom-6 left-2 right-2 px-1">
            <div class="h-1.5 bg-slate-700 rounded-full overflow-hidden shadow-inner">
              <div
                class="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-emerald-500 transition-all duration-500"
                :style="{ width: `${Math.min(100, object.health ?? 100)}%` }"></div>
            </div>
            <div class="text-center text-[9px] text-white/90 mt-1 font-bold drop-shadow-md">
              {{ object.health ?? 100 }} HP
            </div>
          </div>
          <div v-if="object.label && !object.characterImage && object.faceUp !== false"
            class="absolute bottom-1 left-0 right-0 text-center">
            <span class="text-[9px] px-1.5 py-0.5 rounded bg-black/50 text-white backdrop-blur-sm font-medium">{{
              object.label }}</span>
          </div>
        </template>

        <template v-else-if="object.type === 'counter'">
          <div
            class="w-full h-full flex flex-col items-center justify-center cursor-pointer hover:scale-105 active:scale-95 transition-transform duration-200 relative"
            :style="{ background: `linear-gradient(135deg, ${object.color || '#f59e0b'}cc, ${object.color || '#f59e0b'}88)` }"
            @click="changeCounter(1)">
            <div class="text-3xl mb-0.5 drop-shadow-lg">🪙</div>
            <div class="text-white font-bold text-xl drop-shadow-md">{{ object.count ?? 0 }}</div>
            <div class="text-white/80 text-[10px] font-medium">шт</div>
            <div v-if="object.label" class="absolute bottom-1 left-0 right-0 text-center">
              <span class="text-[9px] px-1.5 py-0.5 rounded bg-black/40 text-white backdrop-blur-sm">{{ object.label
                }}</span>
            </div>
          </div>
        </template>

        <template v-else-if="object.url">
          <img :src="object.url" class="w-full h-full object-contain" draggable="false" />
        </template>

        <template v-else>
          <div v-if="object.label && object.faceUp !== false" class="absolute bottom-2 left-0 right-0 text-center">
            <span
              class="text-[10px] font-medium px-2 py-1 rounded-full bg-black/40 text-slate-200 backdrop-blur-sm border border-white/10">{{
              object.label }}</span>
          </div>
        </template>
      </div>

      <template v-if="isSelected">
        <div
          class="absolute -top-1.5 -left-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_12px_rgba(139,92,246,0.9)] border-2 border-slate-900">
        </div>
        <div
          class="absolute -top-1.5 -right-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_12px_rgba(139,92,246,0.9)] border-2 border-slate-900">
        </div>
        <div
          class="absolute -bottom-1.5 -left-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_12px_rgba(139,92,246,0.9)] border-2 border-slate-900">
        </div>
        <div
          class="absolute -bottom-1.5 -right-1.5 w-3 h-3 rounded-full bg-violet-400 shadow-[0_0_12px_rgba(139,92,246,0.9)] border-2 border-slate-900">
        </div>
      </template>

      <div
        class="absolute -top-14 left-1/2 -translate-x-1/2 flex gap-1.5 bg-slate-900/95 backdrop-blur-xl rounded-xl p-1.5 shadow-2xl border border-white/10 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0 z-30">
        <button v-if="object.type === 'card'" @click.stop="handleFlip"
          class="p-2 rounded-lg hover:bg-amber-500/20 text-slate-300 hover:text-amber-300 transition-colors"
          :title="object.faceUp === false ? 'Повернуть лицом вверх' : 'Повернуть лицом вниз'">
          <FlipVertical class="w-4 h-4" />
        </button>
        <button @click.stop="handleRotate"
          class="p-2 rounded-lg hover:bg-violet-500/20 text-slate-300 hover:text-violet-300 transition-colors"
          title="Повернуть">
          <RotateCcw class="w-4 h-4" />
        </button>
        <button v-if="!isDeck" @click.stop="handleDuplicate"
          class="p-2 rounded-lg hover:bg-cyan-500/20 text-slate-300 hover:text-cyan-300 transition-colors"
          title="Копировать">
          <Copy class="w-4 h-4" />
        </button>
        <button v-if="object.type === 'card'" @click.stop="handleAddHand"
          class="p-2 rounded-lg hover:bg-orange-500/20 text-slate-300 hover:text-orange-300 transition-colors"
          title="Взять в руку">
          <Hand class="w-4 h-4" />
        </button>
        <button v-if="isDeck && deckCardCount > 0" @click.stop="handleDrawFromDeck"
          class="p-2 rounded-lg hover:bg-emerald-500/20 text-slate-300 hover:text-emerald-300 transition-colors"
          title="Достать карту">
          <Plus class="w-4 h-4" />
        </button>
        <button v-if="isDeck && deckCardCount > 1" @click.stop="handleShuffleDeck"
          class="p-2 rounded-lg hover:bg-blue-500/20 text-slate-300 hover:text-blue-300 transition-colors"
          title="Перемешать">
          <Shuffle class="w-4 h-4" />
        </button>
        <button v-if="isDeck && deckCardCount > 0" @click.stop="handleSpreadDeck"
          class="p-2 rounded-lg hover:bg-orange-500/20 text-slate-300 hover:text-orange-300 transition-colors"
          title="Разложить">
          <LayoutGrid class="w-4 h-4" />
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
        class="fixed bg-slate-900/95 backdrop-blur-xl rounded-2xl shadow-2xl py-2 z-[200] min-w-[220px] border border-white/10 animate-slide-in"
        :style="{ left: `${contextMenuPosition.x}px`, top: `${contextMenuPosition.y}px` }" @click.stop>
        <div
          class="px-4 py-2.5 text-xs font-semibold text-slate-400 border-b border-white/10 mb-1.5 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-violet-500"></span>
          {{ object.label || object.type }}
        </div>
        <button @click="handleDuplicate"
          class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-violet-500/10 hover:text-violet-300 flex items-center gap-3 transition-colors rounded-lg mx-1">
          <Copy class="w-4 h-4" /> Копировать
        </button>
        <button v-if="object.type === 'card'" @click="handleFlip"
          class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-amber-500/10 hover:text-amber-300 flex items-center gap-3 transition-colors rounded-lg mx-1">
          <FlipVertical class="w-4 h-4" /> {{ object.faceUp === false ? 'Повернуть лицом вверх' : 'Повернуть лицом вниз'
          }}
        </button>
        <button v-if="object.stackId" @click="emit('stack-remove', object.id); showContextMenu.value = false"
          class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-orange-500/10 hover:text-orange-300 flex items-center gap-3 transition-colors rounded-lg mx-1">
          <Layers class="w-4 h-4" /> Убрать из стопки
        </button>
        <button @click="toggleObjectLock"
          :class="['w-full px-4 py-2.5 text-left text-sm flex items-center gap-3 transition-colors rounded-lg mx-1', object.locked ? 'text-amber-400 hover:bg-amber-500/10' : 'text-slate-300 hover:bg-slate-500/10']">
          <Lock class="w-4 h-4" />
          {{ object.locked ? 'Открепить' : 'Закрепить' }}
        </button>
        <button @click="handleRotate"
          class="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-cyan-500/10 hover:text-cyan-300 flex items-center gap-3 transition-colors rounded-lg mx-1">
          <RotateCcw class="w-4 h-4" /> Повернуть на 90°
        </button>
        <hr class="border-white/10 my-1.5" />
        <button @click="handleDelete"
          class="w-full px-4 py-2.5 text-left text-sm text-red-400 hover:bg-red-500/10 flex items-center gap-3 transition-colors rounded-lg mx-1">
          <Trash2 class="w-4 h-4" /> Удалить
        </button>
        <button @click="closeContextMenu"
          class="w-full px-4 py-2 text-left text-xs text-slate-500 hover:text-slate-400 mt-1.5 rounded-lg mx-1">
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