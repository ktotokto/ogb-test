<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWebSocket } from '@vueuse/core'
import { useStorage, useToggle, useDebounce } from '@vueuse/core'
import { 
  Dice5, Cards, SkipForward, ZoomIn, ZoomOut, Maximize,
  MousePointer2, Hand, Pencil, Type
} from 'lucide-vue-next'
import { Stage, Layer, Rect, Group } from 'vue-konva'
import { 
  Dialog,
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { toast } from 'vue-sonner'

// Components
import GameHeader from './GameHeader.vue'
import GameHand from './GameHand.vue'
import PlayerList from './sidebar/PlayerList.vue'
import ObjectLibrary from './sidebar/ObjectLibrary.vue'
import ObjectProperties from './sidebar/ObjectProperties.vue'
import GameChat from './sidebar/GameChat.vue'
import GameObjectRenderer from './GameObjectRenderer.vue'
import DiceRoller from './DiceRoller.vue'
import ContextMenu from './ContextMenu.vue'
import ToolButton from './ToolButton.vue'
import InviteModal from './modals/InviteModal.vue'
import SettingsModal from './modals/SettingsModal.vue'

// Setup
const route = useRoute()
const router = useRouter()
const gameStore = useGameStore()
const userStore = useUserStore()

const sessionId = route.params.sessionId
const currentUser = computed(() => userStore.currentUser)

// State
const showLeftSidebar = ref(true)
const showRightSidebar = ref(true)
const [showInviteModal, toggleInviteModal] = useToggle(false)
const [showSettingsModal, toggleSettingsModal] = useToggle(false)
const [showLeaveConfirm, toggleLeaveConfirm] = useToggle(false)
const currentTool = ref('select')
const selectedObjects = ref(new Set())
const zoom = ref(1)
const boardWidth = ref(window.innerWidth)
const boardHeight = ref(window.innerHeight - 200)

// Game State
const players = computed(() => gameStore.players)
const gameObjects = computed(() => gameStore.objects)
const chatMessages = computed(() => gameStore.chatMessages)
const playerHand = computed(() => gameStore.playerHand)
const gameSettings = computed(() => gameStore.settings)
const gameTimer = computed(() => gameStore.timer)
const isMyTurn = computed(() => gameStore.currentPlayerId === currentUser.value?.id)
const currentPlayer = computed(() => gameStore.currentPlayer)

// Context Menu
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  objectId: null
})

const contextMenuItems = [
  { id: 'copy', label: 'Копировать', icon: 'copy' },
  { id: 'delete', label: 'Удалить', icon: 'trash' },
  { id: 'properties', label: 'Свойства', icon: 'settings' },
  { id: 'front', label: 'На передний план', icon: 'layer-up' },
  { id: 'back', label: 'На задний план', icon: 'layer-down' }
]

// Tools
const tools = [
  { id: 'select', icon: MousePointer2, label: 'Выделение' },
  { id: 'pan', icon: Hand, label: 'Перемещение' },
  { id: 'draw', icon: Pencil, label: 'Рисование' },
  { id: 'text', icon: Type, label: 'Текст' }
]

// WebSocket
const { send: wsSend, data: wsData } = useWebSocket(
  `ws://localhost:5000/game/${sessionId}`,
  {
    autoReconnect: true,
    heartbeat: {
      message: 'ping',
      interval: 30000,
    },
    onConnected: () => {
      wsSend(JSON.stringify({
        type: 'join',
        user: currentUser.value
      }))
    }
  }
)

// Watch WebSocket data
watch(wsData, (data) => {
  if (data) {
    const message = JSON.parse(data)
    handleWebSocketMessage(message)
  }
})

// Methods
const handleWebSocketMessage = (message) => {
  switch (message.type) {
    case 'game:update':
      gameStore.updateState(message.payload)
      break
    case 'object:created':
      gameStore.addObject(message.payload)
      break
    case 'object:moved':
      gameStore.updateObject(message.payload)
      break
    case 'object:deleted':
      gameStore.removeObject(message.payload.objectId)
      break
    case 'player:joined':
      gameStore.addPlayer(message.payload)
      toast.success(`${message.payload.name} присоединился`)
      break
    case 'player:left':
      gameStore.removePlayer(message.payload.userId)
      break
    case 'chat:message':
      gameStore.addChatMessage(message.payload)
      break
    case 'dice:rolled':
      handleDiceRoll(message.payload)
      break
  }
}

const sendAction = (type, payload) => {
  wsSend(JSON.stringify({ type, payload }))
}

// Object Actions
const handleObjectClick = (event, obj) => {
  if (event.evt.ctrlKey || event.evt.metaKey) {
    selectedObjects.value.add(obj.id)
  } else {
    selectedObjects.value = new Set([obj.id])
  }
}

const handleObjectDrag = useDebounce((obj, event) => {
  sendAction('object:move', {
    objectId: obj.id,
    position: {
      x: event.target.x(),
      y: event.target.y()
    }
  })
}, 100)

const handleBoardClick = () => {
  selectedObjects.value.clear()
  contextMenu.value.visible = false
}

const addObjectToBoard = (type, data) => {
  const newObj = {
    id: `obj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    type,
    position: {
      x: boardWidth.value / 2,
      y: boardHeight.value / 2
    },
    rotation: 0,
    scale: 1,
    owner: currentUser.value.id,
    ...data
  }
  
  sendAction('object:create', newObj)
  toast.success('Объект добавлен')
}

const uploadObject = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    })
    const data = await response.json()
    addObjectToBoard(data.type, { url: data.url })
  } catch (error) {
    toast.error('Ошибка загрузки файла')
  }
}

const updateObjectProperties = (objectId, properties) => {
  sendAction('object:update', { objectId, properties })
}

const deleteSelectedObjects = () => {
  selectedObjects.value.forEach(id => {
    sendAction('object:delete', { objectId: id })
  })
  selectedObjects.value.clear()
  toast.success('Объекты удалены')
}

const isDraggable = (obj) => {
  return currentTool.value === 'select' && 
         (obj.owner === currentUser.value.id || gameStore.isAdmin)
}

// Game Actions
const rollDice = () => {
  sendAction('dice:roll', {
    count: 2,
    playerId: currentUser.value.id
  })
}

const handleDiceRoll = (payload) => {
  // Show dice animation
  toast.info(`Выпало: ${payload.results.join(', ')}`)
}

const drawCard = () => {
  sendAction('card:draw', {
    playerId: currentUser.value.id,
    count: 1
  })
}

const playCard = (card) => {
  sendAction('card:play', {
    cardId: card.id,
    playerId: currentUser.value.id
  })
}

const endTurn = () => {
  sendAction('turn:end', {
    playerId: currentUser.value.id
  })
}

// UI Actions
const toggleSidebar = (side) => {
  if (side === 'left') showLeftSidebar.value = !showLeftSidebar.value
  if (side === 'right') showRightSidebar.value = !showRightSidebar.value
}

const zoomIn = () => zoom.value = Math.min(zoom.value + 0.1, 3)
const zoomOut = () => zoom.value = Math.max(zoom.value - 0.1, 0.1)
const resetZoom = () => zoom.value = 1

const showContextMenu = (event, obj) => {
  event.evt.preventDefault()
  contextMenu.value = {
    visible: true,
    x: event.evt.clientX,
    y: event.evt.clientY,
    objectId: obj.id
  }
}

const handleContextMenuSelect = (action) => {
  switch (action) {
    case 'delete':
      deleteSelectedObjects()
      break
    case 'copy':
      copySelectedObjects()
      break
  }
  contextMenu.value.visible = false
}

const copySelectedObjects = () => {
  selectedObjects.value.forEach(id => {
    const obj = gameStore.objects.find(o => o.id === id)
    if (obj) {
      addObjectToBoard(obj.type, {
        ...obj,
        position: {
          x: obj.position.x + 20,
          y: obj.position.y + 20
        }
      })
    }
  })
}

const saveGame = async () => {
  try {
    await fetch(`/api/game/${sessionId}/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(gameStore.state)
    })
    toast.success('Игра сохранена')
  } catch (error) {
    toast.error('Ошибка сохранения')
  }
}

const confirmLeave = () => toggleLeaveConfirm(true)

const leaveGame = async () => {
  sendAction('game:leave', { userId: currentUser.value.id })
  await router.push('/games')
  toast.success('Вы покинули игру')
}

const sendMessage = (text) => {
  sendAction('chat:send', {
    text,
    userId: currentUser.value.id,
    userName: currentUser.value.name
  })
}

// Lifecycle
onMounted(() => {
  const handleResize = () => {
    boardWidth.value = window.innerWidth
    boardHeight.value = window.innerHeight - 200
  }
  
  window.addEventListener('resize', handleResize)
  handleResize()
  
  gameStore.loadGame(sessionId)
})

onUnmounted(() => {
  sendAction('game:leave', { userId: currentUser.value.id })
})

// Computed
const selectedObjectData = computed(() => {
  if (selectedObjects.value.size === 0) return null
  const id = Array.from(selectedObjects.value)[0]
  return gameStore.objects.find(o => o.id === id)
})

const showDiceRoller = ref(false)
const dicePosition = ref({ x: 0, y: 0 })

const handleDiceRollComplete = () => {
  showDiceRoller.value = false
}
</script>


<template>
  <div class="h-screen w-screen bg-slate-900 text-white flex flex-col overflow-hidden">
    <GameHeader 
      :session-id="sessionId"
      :timer="gameTimer"
      @save="saveGame"
      @invite="showInviteModal = true"
      @leave="confirmLeave"
      @toggle-sidebar="toggleSidebar"
    />

    <div class="flex-1 flex overflow-hidden relative">
      <transition 
        enter-active-class="transition-transform duration-300 ease-out"
        enter-from-class="-translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transition-transform duration-300 ease-in"
        leave-from-class="translate-x-0"
        leave-to-class="-translate-x-full"
      >
        <div v-if="showLeftSidebar" class="w-80 bg-slate-800/95 backdrop-blur border-r border-slate-700 flex flex-col">
          <PlayerList :players="players" :current-user="currentUser" />
          <GameChat :messages="chatMessages" @send="sendMessage" />
        </div>
      </transition>

      <div class="flex-1 relative bg-slate-950">
        <VueKonva
          ref="stage"
          :width="boardWidth"
          :height="boardHeight"
          class="absolute inset-0"
          @click="handleBoardClick"
        >
          <v-layer>
            <v-rect
              v-if="gameSettings.showGrid"
              :width="boardWidth"
              :height="boardHeight"
              :fill="gameSettings.gridColor"
            />
            <v-grid
              v-if="gameSettings.showGrid"
              :width="boardWidth"
              :height="boardHeight"
              :cell-size="gameSettings.gridSize"
            />
          </v-layer>
>
          <v-layer ref="objectsLayer">
            <v-group
              v-for="obj in gameObjects"
              :key="obj.id"
              :id="obj.id"
              :x="obj.position.x"
              :y="obj.position.y"
              :rotation="obj.rotation"
              :scale-x="obj.scale"
              :scale-y="obj.scale"
              :draggable="isDraggable(obj)"
              @click="handleObjectClick($event, obj)"
              @dragend="handleObjectDrag(obj, $event)"
              @contextmenu="showContextMenu($event, obj)"
            >
              <GameObjectRenderer :object="obj" :selected="selectedObjects.has(obj.id)" />
            </v-group>
          </v-layer>
        </VueKonva>

        <DiceRoller
          v-if="showDiceRoller"
          :position="dicePosition"
          @complete="handleDiceRollComplete"
        />

        <ContextMenu
          v-if="contextMenu.visible"
          :x="contextMenu.x"
          :y="contextMenu.y"
          :items="contextMenuItems"
          @select="handleContextMenuSelect"
          @close="contextMenu.visible = false"
        />
      </div>

      <transition
        enter-active-class="transition-transform duration-300 ease-out"
        enter-from-class="translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transition-transform duration-300 ease-in"
        leave-from-class="translate-x-0"
        leave-to-class="translate-x-full"
      >
        <div v-if="showRightSidebar" class="w-80 bg-slate-800/95 backdrop-blur border-l border-slate-700 flex flex-col">
          <ObjectLibrary @add="addObjectToBoard" @upload="uploadObject" />
          <ObjectProperties
            v-if="selectedObjects.size > 0"
            :object="selectedObjectData"
            @update="updateObjectProperties"
            @delete="deleteSelectedObjects"
          />
        </div>
      </transition>
    </div>

    <GameHand
      v-if="playerHand.length"
      :cards="playerHand"
      class="absolute bottom-20 left-1/2 -translate-x-1/2"
      @play="playCard"
    />

    <div class="h-16 bg-slate-800 border-t border-slate-700 flex items-center justify-between px-4 gap-4">
      <div class="flex items-center gap-2">
        <ToolButton
          v-for="tool in tools"
          :key="tool.id"
          :tool="tool"
          :active="currentTool === tool.id"
          @click="currentTool = tool.id"
        />
      </div>

      <div class="flex items-center gap-3">
        <Button
          v-if="isMyTurn"
          variant="primary"
          size="sm"
          @click="rollDice"
          :disabled="showDiceRoller"
        >
          <Dice5 class="w-4 h-4 mr-2" />
          Бросить кубик
        </Button>

        <Button
          v-if="isMyTurn"
          variant="secondary"
          size="sm"
          @click="drawCard"
          :disabled="playerHand.length >= 10"
        >
          <Cards class="w-4 h-4 mr-2" />
          Взять карту
        </Button>

        <Button
          v-if="isMyTurn"
          variant="success"
          size="sm"
          @click="endTurn"
        >
          <SkipForward class="w-4 h-4 mr-2" />
          Завершить ход
        </Button>
      </div>

      <div class="flex items-center gap-2">
        <Button variant="ghost" size="icon" @click="zoomOut">
          <ZoomOut class="w-4 h-4" />
        </Button>
        <span class="text-sm w-12 text-center">{{ Math.round(zoom * 100) }}%</span>
        <Button variant="ghost" size="icon" @click="zoomIn">
          <ZoomIn class="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon" @click="resetZoom">
          <Maximize class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <Dialog v-model:open="showInviteModal">
      <InviteModal :session-id="sessionId" @close="showInviteModal = false" />
    </Dialog>

    <Dialog v-model:open="showSettingsModal">
      <SettingsModal v-model:settings="gameSettings" @close="showSettingsModal = false" />
    </Dialog>

    <AlertDialog v-model:open="showLeaveConfirm">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Покинуть игру?</AlertDialogTitle>
          <AlertDialogDescription>
            Вы уверены, что хотите покинуть игровую сессию?
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Отмена</AlertDialogCancel>
          <AlertDialogAction @click="leaveGame">Покинуть</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>

<style>
* {
  @apply box-border;
}

body {
  @apply bg-slate-900 text-white;
}
</style>