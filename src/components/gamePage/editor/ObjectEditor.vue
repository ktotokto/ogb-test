<script setup>
import { ref, computed } from 'vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useGameWebSocket } from '@/composables/useGameWebSocket'
import { Plus, Trash2, Search, Square, Circle, Type, Image } from 'lucide-vue-next'

const gameStore = useGameStore()
const userStore = useUserStore()
const { socket } = useGameWebSocket()

const searchQuery = ref('')
const selectedType = ref('card')

const objectTypes = [
  { id: 'card', label: 'Карта', icon: Square },
  { id: 'token', label: 'Жетон', icon: Circle },
  { id: 'text', label: 'Текст', icon: Type },
  { id: 'image', label: 'Изображение', icon: Image }
]

const objects = computed(() => {
  let filtered = gameStore.objects || []
  if (searchQuery.value) {
    filtered = filtered.filter(obj =>
      obj.label?.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  return filtered
})

const createObject = (type) => {
  const newObject = {
    id: `obj_${Date.now()}`,
    type,
    label: `Новый ${type}`,
    position: { x: 50000, y: 50000 },
    width: type === 'card' ? 120 : 100,
    height: type === 'card' ? 180 : 100,
    rotation: 0,
    owner: userStore.userId,
    ownerId: userStore.userId,
    inHand: false,
    faceUp: true
  }
  
  gameStore.addObject(newObject)
  
  if (socket.value && gameStore.sessionId) {
    socket.value.emit('object:create', {
      sessionId: gameStore.sessionId,
      object: newObject
    })
  }
}

const deleteObject = (objectId) => {
  if (!confirm('Удалить объект?')) return
  gameStore.removeObject(objectId)
  if (socket.value && gameStore.sessionId) {
    socket.value.emit('object:delete', {
      sessionId: gameStore.sessionId,
      objectId
    })
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 gap-2">
      <button
        v-for="type in objectTypes"
        :key="type.id"
        @click="createObject(type.id)"
        class="p-3 bg-slate-800/60 hover:bg-slate-700 border border-white/5 hover:border-violet-500/50 rounded-lg transition-all flex flex-col items-center gap-2"
      >
        <component :is="type.icon" class="w-5 h-5 text-violet-400" />
        <span class="text-xs text-slate-300">{{ type.label }}</span>
      </button>
    </div>

    <div class="relative">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Поиск объектов..."
        class="w-full px-4 py-2 pl-10 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white placeholder-slate-400 focus:outline-none focus:border-violet-500"
      />
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
    </div>

    <div class="max-h-64 overflow-y-auto space-y-2">
      <div
        v-for="obj in objects"
        :key="obj.id"
        class="p-3 bg-slate-800/40 border border-white/5 rounded-lg flex items-center justify-between"
      >
        <div>
          <h4 class="text-sm font-medium text-white">{{ obj.label }}</h4>
          <p class="text-xs text-slate-400">{{ obj.type }} • {{ obj.width }}x{{ obj.height }}</p>
        </div>
        <button
          @click="deleteObject(obj.id)"
          class="p-2 bg-red-600/50 hover:bg-red-500 text-white rounded transition-all"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
      <div v-if="objects.length === 0" class="text-center py-8 text-slate-400">
        <p class="text-sm">Нет объектов</p>
      </div>
    </div>
  </div>
</template>