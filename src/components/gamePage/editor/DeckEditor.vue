<script setup>
import { ref, computed } from 'vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useGameWebSocket } from '@/composables/useGameWebSocket'
import { Plus, Trash2, Save, Edit2, Copy, Search, Layers, X } from 'lucide-vue-next'

const gameStore = useGameStore()
const userStore = useUserStore()
const { socket } = useGameWebSocket()

const emit = defineEmits(['close'])

const isCreating = ref(false)
const editingDeck = ref(null)
const searchQuery = ref('')
const newDeckName = ref('')
const selectedCards = ref([])

const decks = computed(() => gameStore.decks || [])

const filteredDecks = computed(() => {
  if (!searchQuery.value) return decks.value
  return decks.value.filter(deck =>
    deck.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const availableCards = computed(() => {
  return gameStore.objects.filter(obj => obj.type === 'card')
})

const startCreateDeck = () => {
  editingDeck.value = null
  newDeckName.value = ''
  selectedCards.value = []
  isCreating.value = true
}

const startEditDeck = (deck) => {
  editingDeck.value = { ...deck }
  newDeckName.value = deck.name
  selectedCards.value = deck.cards || []
  isCreating.value = true
}

const saveDeck = () => {
  if (!newDeckName.value.trim()) return

  const deckData = {
    id: editingDeck.value?.id || `deck_${Date.now()}`,
    name: newDeckName.value,
    cards: selectedCards.value,
    createdAt: new Date().toISOString(),
    createdBy: userStore.userId
  }

  if (editingDeck.value) {
    gameStore.updateDeck(editingDeck.value.id, deckData)
  } else {
    gameStore.addDeck(deckData)
  }

  if (socket.value && gameStore.sessionId) {
    socket.value.emit('deck:save', {
      sessionId: gameStore.sessionId,
      deck: deckData
    })
  }

  isCreating.value = false
  editingDeck.value = null
  newDeckName.value = ''
  selectedCards.value = []
}

const cancelEdit = () => {
  isCreating.value = false
  editingDeck.value = null
  newDeckName.value = ''
  selectedCards.value = []
}

const deleteDeck = (deckId) => {
  if (!confirm('Удалить эту колоду?')) return
  gameStore.removeDeck(deckId)
  if (socket.value && gameStore.sessionId) {
    socket.value.emit('deck:delete', {
      sessionId: gameStore.sessionId,
      deckId
    })
  }
}

const duplicateDeck = (deck) => {
  const newDeck = {
    ...deck,
    id: `deck_${Date.now()}`,
    name: `${deck.name} (копия)`
  }
  gameStore.addDeck(newDeck)
  if (socket.value && gameStore.sessionId) {
    socket.value.emit('deck:save', {
      sessionId: gameStore.sessionId,
      deck: newDeck
    })
  }
}

const toggleCardSelection = (card) => {
  const index = selectedCards.value.findIndex(c => c.id === card.id)
  if (index !== -1) {
    selectedCards.value.splice(index, 1)
  } else {
    selectedCards.value.push({
      id: card.id,
      label: card.label,
      cardData: card.cardData
    })
  }
}

const removeCardFromDeck = (cardId) => {
  selectedCards.value = selectedCards.value.filter(c => c.id !== cardId)
}

const spawnDeck = (deck) => {
  if (!confirm(`Создать ${deck.cards?.length || 0} карт на поле?`)) return
  
  const centerX = 50000
  const centerY = 50000
  
  deck.cards?.forEach((card, index) => {
    const newCard = {
      id: `card_${Date.now()}_${index}`,
      type: 'card',
      label: card.label,
      position: {
        x: centerX + (index % 5) * 140 - 280,
        y: centerY + Math.floor(index / 5) * 200 - 200
      },
      width: 120,
      height: 180,
      rotation: 0,
      owner: userStore.userId,
      ownerId: userStore.userId,
      inHand: false,
      faceUp: true,
      cardData: card.cardData
    }
    
    gameStore.addObject(newCard)
    
    if (socket.value && gameStore.sessionId) {
      socket.value.emit('object:create', {
        sessionId: gameStore.sessionId,
        object: newCard
      })
    }
  })
}
</script>

<template>
  <div v-if="!isCreating" class="space-y-4">
    <div class="flex items-center gap-2">
      <div class="relative flex-1">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск колод..."
          class="w-full px-4 py-2 pl-10 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white placeholder-slate-400 focus:outline-none focus:border-violet-500"
        />
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
      </div>
      <button
        @click="startCreateDeck"
        class="px-3 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg transition-all flex items-center gap-1 text-sm"
      >
        <Plus class="w-4 h-4" />
        Создать
      </button>
    </div>

    <div v-if="filteredDecks.length === 0" class="text-center py-8 text-slate-400">
      <Layers class="w-12 h-12 mx-auto mb-2 opacity-30" />
      <p>Нет колод</p>
      <p class="text-xs mt-1">Создайте первую колоду</p>
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="deck in filteredDecks"
        :key="deck.id"
        class="p-3 bg-slate-800/40 border border-white/5 rounded-lg hover:border-violet-500/30 transition-all"
      >
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-medium text-white">{{ deck.name }}</h3>
          <span class="text-xs text-slate-400">{{ deck.cards?.length || 0 }} карт</span>
        </div>
        <div class="flex items-center gap-1">
          <button
            @click="startEditDeck(deck)"
            class="flex-1 px-2 py-1.5 bg-slate-700/50 hover:bg-slate-600 text-slate-300 rounded text-xs transition-all flex items-center justify-center gap-1"
          >
            <Edit2 class="w-3 h-3" />
            Редактировать
          </button>
          <button
            @click="duplicateDeck(deck)"
            class="px-2 py-1.5 bg-slate-700/50 hover:bg-slate-600 text-slate-300 rounded text-xs transition-all"
          >
            <Copy class="w-3 h-3" />
          </button>
          <button
            @click="spawnDeck(deck)"
            class="px-2 py-1.5 bg-emerald-600/50 hover:bg-emerald-500 text-white rounded text-xs transition-all"
          >
            <Plus class="w-3 h-3" />
          </button>
          <button
            @click="deleteDeck(deck.id)"
            class="px-2 py-1.5 bg-red-600/50 hover:bg-red-500 text-white rounded text-xs transition-all"
          >
            <Trash2 class="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="font-semibold text-white">
        {{ editingDeck ? 'Редактировать колоду' : 'Новая колода' }}
      </h3>
      <button @click="cancelEdit" class="text-slate-400 hover:text-white">
        <X class="w-5 h-5" />
      </button>
    </div>

    <input
      v-model="newDeckName"
      type="text"
      placeholder="Название колоды"
      class="w-full px-4 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white placeholder-slate-400 focus:outline-none focus:border-violet-500"
    />

    <div class="border border-white/10 rounded-lg overflow-hidden">
      <div class="p-2 bg-slate-800/60 border-b border-white/10 flex items-center justify-between">
        <span class="text-xs font-medium text-slate-300">Карты в колоде ({{ selectedCards.length }})</span>
      </div>
      <div class="max-h-32 overflow-y-auto p-2 space-y-1">
        <div v-if="selectedCards.length === 0" class="text-center py-4 text-slate-400 text-xs">
          Нет карт в колоде
        </div>
        <div
          v-for="card in selectedCards"
          :key="card.id"
          class="flex items-center justify-between p-2 bg-slate-700/30 rounded text-xs"
        >
          <span class="text-slate-300 truncate flex-1">{{ card.label }}</span>
          <button @click="removeCardFromDeck(card.id)" class="text-red-400 hover:text-red-300 ml-2">
            <X class="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>

    <div class="border border-white/10 rounded-lg overflow-hidden">
      <div class="p-2 bg-slate-800/60 border-b border-white/10">
        <span class="text-xs font-medium text-slate-300">Доступные карты</span>
      </div>
      <div class="max-h-40 overflow-y-auto p-2 grid grid-cols-2 gap-2">
        <div
          v-for="card in availableCards"
          :key="card.id"
          @click="toggleCardSelection(card)"
          :class="[
            'p-2 rounded cursor-pointer transition-all text-xs',
            selectedCards.find(c => c.id === card.id)
              ? 'bg-violet-600/50 border-violet-500 text-white'
              : 'bg-slate-700/30 border-white/5 hover:bg-slate-600/50 text-slate-300'
          ]"
        >
          {{ card.label }}
        </div>
        <div v-if="availableCards.length === 0" class="col-span-2 text-center py-4 text-slate-400 text-xs">
          Нет карт на поле
        </div>
      </div>
    </div>

    <div class="flex gap-2">
      <button
        @click="saveDeck"
        :disabled="!newDeckName.trim()"
        class="flex-1 px-4 py-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-all flex items-center justify-center gap-2 text-sm"
      >
        <Save class="w-4 h-4" />
        Сохранить
      </button>
      <button
        @click="cancelEdit"
        class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-all text-sm"
      >
        Отмена
      </button>
    </div>
  </div>
</template>