<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useGameWebSocket } from '@/composables/useGameWebSocket'
import { Plus, Trash2, Save, Edit2, Copy, Search, Layers, X, Upload, Image as ImageIcon } from 'lucide-vue-next'

const gameStore = useGameStore()
const userStore = useUserStore()
const { socket } = useGameWebSocket()

const emit = defineEmits(['close'])

const isCreating = ref(false)
const editingDeck = ref(null)
const searchQuery = ref('')
const newDeckName = ref('')
const selectedCards = ref([])

const cardImages = ref([])
const cardBackImage = ref(null)
const isUploading = ref(false)
const uploadedCards = ref([])

const cardWidth = ref(120)
const cardHeight = ref(180)
const cardShape = ref('rounded') 

const decks = computed(() => {
  const list = gameStore.decks
  if (!list) return []
  if (list.length === 0 && gameStore.objects) {
    return gameStore.objects
      .filter(o => o.type === 'deck')
      .map(o => ({
        id: o.id,
        name: o.label || o.name || 'Колода',
        cards: o.cards || [],
        cardCount: o.cardCount || 0
      }))
  }
  return list
})

const filteredDecks = computed(() => {
  if (!searchQuery.value) return decks.value
  return decks.value.filter(deck =>
    deck.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const availableCards = computed(() => {
  return gameStore.objects.filter(obj => obj.type === 'card')
})

const handleCardImagesUpload = (event) => {
  const files = Array.from(event.target.files)
  if (files.length === 0) return

  isUploading.value = true
  uploadedCards.value = []

  files.forEach((file, index) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadedCards.value.push({
        id: `temp_${Date.now()}_${index}`,
        file: file,
        image: e.target.result,
        name: file.name.replace(/\.[^/.]+$/, ""),
        label: `Карта ${index + 1}`
      })

      if (uploadedCards.value.length === files.length) {
        isUploading.value = false
      }
    }
    reader.readAsDataURL(file)
  })
}

const handleCardBackUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    cardBackImage.value = { file, image: e.target.result }
  }
  reader.readAsDataURL(file)
}

const removeUploadedCard = (index) => {
  uploadedCards.value.splice(index, 1)
}

const moveUploadedCard = (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= uploadedCards.value.length) return
  const temp = uploadedCards.value[index]
  uploadedCards.value[index] = uploadedCards.value[newIndex]
  uploadedCards.value[newIndex] = temp
}

const startCreateDeck = () => {
  editingDeck.value = null
  newDeckName.value = ''
  selectedCards.value = []
  cardImages.value = []
  cardBackImage.value = null
  uploadedCards.value = []
  cardWidth.value = 120
  cardHeight.value = 180
  cardShape.value = 'rounded'
  isCreating.value = true
}

const startEditDeck = (deck) => {
  editingDeck.value = { ...deck }
  newDeckName.value = deck.name
  selectedCards.value = deck.cards || []
  if (deck.cardFormat) {
    cardWidth.value = deck.cardFormat.width || 120
    cardHeight.value = deck.cardFormat.height || 180
    cardShape.value = deck.cardFormat.shape || 'rounded'
  } else {
    cardWidth.value = 120
    cardHeight.value = 180
    cardShape.value = 'rounded'
  }
  isCreating.value = true
}

const createDeckFromImages = async () => {
  if (!newDeckName.value.trim()) return alert('Введите название колоды!')
  if (uploadedCards.value.length === 0) return alert('Загрузите хотя бы одну карту!')

  isUploading.value = true

  try {
    const deckCards = []
    const centerX = 50000
    const centerY = 50000
    const cardsPerRow = 5
    const spacingX = cardWidth.value + 20
    const spacingY = cardHeight.value + 20

    for (let i = 0; i < uploadedCards.value.length; i++) {
      const uploadedCard = uploadedCards.value[i]
      const row = Math.floor(i / cardsPerRow)
      const col = i % cardsPerRow

      const newCard = {
        id: `card_${Date.now()}_${i}`,
        type: 'card',
        label: uploadedCard.label || `Карта ${i + 1}`,
        position: {
          x: centerX + (col * spacingX) - ((Math.min(uploadedCards.value.length, cardsPerRow) * spacingX) / 2) + spacingX / 2,
          y: centerY + (row * spacingY) - 200
        },
        width: cardWidth.value,
        height: cardHeight.value,
        shape: cardShape.value,
        rotation: 0,
        ownerId: userStore.userId,
        inHand: false,
        faceUp: true,
        cardData: {
          name: uploadedCard.label || `Карта ${i + 1}`,
          frontImage: uploadedCard.image,
          backImage: cardBackImage.value?.image || null
        }
      }

      deckCards.push({
        id: newCard.id,
        label: newCard.label,
        cardData: newCard.cardData
      })

      await new Promise(resolve => setTimeout(resolve, 30))
    }

    const deckData = {
      id: `deck_${Date.now()}`,
      lable: newDeckName.value,
      cards: deckCards,
      cardCount: deckCards.length,
      hasCustomBack: !!cardBackImage.value,
      createdAt: new Date().toISOString(),
      createdBy: userStore.userId,
      cardFormat: { 
        width: cardWidth.value,
        height: cardHeight.value,
        shape: cardShape.value
      }
    }

    gameStore.addDeck(deckData)

    if (socket.value && gameStore.sessionId) {
      socket.value.emit('deck:create', {
        sessionId: gameStore.sessionId,
        deck: deckData
      })
    }

    uploadedCards.value = []
    cardBackImage.value = null
    newDeckName.value = ''
    cardWidth.value = 120
    cardHeight.value = 180
    cardShape.value = 'rounded'
    isCreating.value = false

    alert(`Создано ${deckCards.length} карт и колода "${deckData.name}"!`)

  } catch (error) {
    console.error('Ошибка создания колоды:', error)
    alert('Ошибка при создании колоды: ' + error.message)
  } finally {
    isUploading.value = false
  }
}

const selectDeckToAdd = (deck) => {
  emit('select-deck', deck)
}

const saveDeck = () => {
  if (!newDeckName.value.trim()) return alert('Введите название колоды!')

  const deckData = {
    id: editingDeck.value?.id || `deck_${Date.now()}`,
    label: newDeckName.value.trim(),
    cards: selectedCards.value,
    cardCount: selectedCards.value.length,
    cardFormat: {
      width: cardWidth.value,
      height: cardHeight.value,
      shape: cardShape.value
    }
  }

  if (editingDeck.value) {
    socket.value?.emit('deck:update', { sessionId: gameStore.sessionId, deck: deckData })
  } else {
    gameStore.addDeck(deckData)
    socket.value?.emit('deck:create', { sessionId: gameStore.sessionId, deck: deckData })
  }

  cancelEdit()
}

const cancelEdit = () => {
  isCreating.value = false
  editingDeck.value = null
  newDeckName.value = ''
  selectedCards.value = []
  uploadedCards.value = []
  cardBackImage.value = null
  cardWidth.value = 120
  cardHeight.value = 180
  cardShape.value = 'rounded'
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
    label: `${deck.label} (копия)`,
    cardFormat: deck.cardFormat || { width: 120, height: 180, shape: 'rounded' }
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
</script>

<template>
  <div v-if="!isCreating" class="space-y-4">
    <div class="flex items-center gap-2">
      <div class="relative flex-1">
        <input v-model="searchQuery" type="text" placeholder="Поиск колод..."
          class="w-full px-4 py-2 pl-10 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white placeholder-slate-400 focus:outline-none focus:border-violet-500" />
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
      </div>
      <button @click="startCreateDeck"
        class="px-3 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg transition-all flex items-center gap-1 text-sm">
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
      <div v-for="deck in filteredDecks" :key="deck.id"
        class="p-3 bg-slate-800/40 border border-white/5 rounded-lg hover:border-violet-500/30 transition-all">
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-medium text-white">{{ deck.name }}</h3>
          <span class="text-xs text-slate-400">{{ deck.cards?.length || 0 }} карт</span>
        </div>
        <div class="flex items-center gap-1">
          <button @click="startEditDeck(deck)"
            class="flex-1 px-2 py-1.5 bg-slate-700/50 hover:bg-slate-600 text-slate-300 rounded text-xs transition-all flex items-center justify-center gap-1">
            <Edit2 class="w-3 h-3" />
            Редактировать
          </button>
          <button @click="duplicateDeck(deck)"
            class="px-2 py-1.5 bg-slate-700/50 hover:bg-slate-600 text-slate-300 rounded text-xs transition-all">
            <Copy class="w-3 h-3" />
          </button>
          <button @click="deleteDeck(deck.id)"
            class="px-2 py-1.5 bg-red-600/50 hover:bg-red-500 text-white rounded text-xs transition-all">
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

    <div class="space-y-4 p-4 bg-slate-800/30 border border-violet-500/30 rounded-lg">
      <h4 class="text-sm font-medium text-violet-300 flex items-center gap-2">
        <Upload class="w-4 h-4" />
        Создание из изображений
      </h4>

      <input v-model="newDeckName" type="text" placeholder="Название колоды *"
        class="w-full px-4 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white placeholder-slate-400 focus:outline-none focus:border-violet-500" />

      <div class="p-3 bg-slate-800/40 border border-white/10 rounded-lg space-y-3">
        <h5 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Формат карт</h5>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-slate-400 mb-1 block">Ширина (px)</label>
            <input v-model.number="cardWidth" type="number" min="50" max="500"
              class="w-full px-3 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:border-violet-500" />
          </div>
          <div>
            <label class="text-xs text-slate-400 mb-1 block">Высота (px)</label>
            <input v-model.number="cardHeight" type="number" min="50" max="500"
              class="w-full px-3 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:border-violet-500" />
          </div>
        </div>
        <div>
          <label class="text-xs text-slate-400 mb-2 block">Форма</label>
          <div class="flex gap-2">
            <button v-for="shape in ['square', 'rounded', 'circle']" :key="shape" @click="cardShape = shape" :class="[
              'flex-1 py-2 text-xs font-medium rounded-lg border transition-all',
              cardShape === shape
                ? 'bg-violet-600/80 border-violet-500 text-white shadow-lg shadow-violet-500/20'
                : 'bg-slate-800/60 border-white/10 text-slate-400 hover:border-violet-500/50'
            ]">
              {{ shape === 'square' ? 'Квадрат' : shape === 'rounded' ? 'Скруглённая' : 'Круг' }}
            </button>
          </div>
        </div>
        <div class="flex justify-center pt-1">
          <div
            class="border border-white/20 bg-slate-700/50 flex items-center justify-center text-[10px] text-slate-400"
            :style="{
              width: Math.min(cardWidth, 80) + 'px',
              height: Math.min(cardHeight, 100) + 'px',
              borderRadius: cardShape === 'circle' ? '50%' : cardShape === 'rounded' ? '8px' : '0px'
            }">
            Превью
          </div>
        </div>
      </div>

      <div class="space-y-2">
        <label class="text-xs text-slate-400">Рубашка карт (необязательно)</label>
        <div v-if="cardBackImage" class="relative w-full h-24 bg-slate-700/50 rounded-lg overflow-hidden">
          <img :src="cardBackImage.image" class="w-full h-full object-cover" />
          <button @click="cardBackImage = null"
            class="absolute top-1 right-1 p-1 bg-red-600/80 hover:bg-red-500 rounded text-white">
            <X class="w-3 h-3" />
          </button>
        </div>
        <label v-else
          class="flex items-center justify-center w-full h-24 border-2 border-dashed border-slate-600 hover:border-violet-500 rounded-lg cursor-pointer transition-all">
          <div class="text-center">
            <ImageIcon class="w-6 h-6 mx-auto text-slate-400 mb-1" />
            <span class="text-xs text-slate-400">Загрузить рубашку</span>
          </div>
          <input type="file" @change="handleCardBackUpload" accept="image/*" class="hidden" />
        </label>
      </div>

      <div class="space-y-2">
        <label class="text-xs text-slate-400">Карты (выберите несколько файлов) *</label>
        <label
          class="flex items-center justify-center w-full h-24 border-2 border-dashed border-slate-600 hover:border-violet-500 rounded-lg cursor-pointer transition-all">
          <div class="text-center">
            <Upload class="w-6 h-6 mx-auto text-slate-400 mb-1" />
            <span class="text-xs text-slate-400">Выберите изображения карт</span>
          </div>
          <input type="file" @change="handleCardImagesUpload" accept="image/*" multiple class="hidden" />
        </label>
      </div>

      <div v-if="uploadedCards.length > 0" class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs text-slate-400">Загружено карт: {{ uploadedCards.length }}</span>
          <button @click="uploadedCards = []" class="text-xs text-red-400 hover:text-red-300">
            Очистить все
          </button>
        </div>
        <div class="max-h-48 overflow-y-auto space-y-2 p-2 bg-slate-800/40 rounded">
          <div v-for="(card, index) in uploadedCards" :key="card.id"
            class="flex items-center gap-2 p-2 bg-slate-700/30 rounded">
            <img :src="card.image" class="w-10 h-14 object-cover rounded" />
            <div class="flex-1 min-w-0">
              <input v-model="card.label" type="text" placeholder="Название карты"
                class="w-full px-2 py-1 bg-slate-600/50 border border-white/10 rounded text-xs text-white placeholder-slate-400" />
            </div>
            <div class="flex flex-col gap-1">
              <button @click="moveUploadedCard(index, -1)" class="p-1 hover:bg-slate-600 rounded text-xs">↑</button>
              <button @click="moveUploadedCard(index, 1)" class="p-1 hover:bg-slate-600 rounded text-xs">↓</button>
            </div>
            <button @click="removeUploadedCard(index)" class="p-1 text-red-400 hover:bg-red-500/20 rounded">
              <X class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      <button @click="createDeckFromImages" :disabled="!newDeckName.trim() || uploadedCards.length === 0 || isUploading"
        class="w-full py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-all flex items-center justify-center gap-2">
        <Upload v-if="!isUploading" class="w-4 h-4" />
        <div v-else class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        {{ isUploading ? 'Создание...' : `Создать ${uploadedCards.length} карт и колоду` }}
      </button>
    </div>

    <div class="border-t border-white/10 pt-4">
      <p class="text-xs text-slate-500 text-center">
        Или используйте ручной выбор карт
      </p>
    </div>

    <div class="border border-white/10 rounded-lg overflow-hidden">
      <div class="p-2 bg-slate-800/60 border-b border-white/10 flex items-center justify-between">
        <span class="text-xs font-medium text-slate-300">Карты в колоде ({{ selectedCards.length }})</span>
      </div>
      <div class="max-h-32 overflow-y-auto p-2 space-y-1">
        <div v-if="selectedCards.length === 0" class="text-center py-4 text-slate-400 text-xs">
          Нет карт в колоде
        </div>
        <div v-for="card in selectedCards" :key="card.id"
          class="flex items-center justify-between p-2 bg-slate-700/30 rounded text-xs">
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
        <div v-for="card in availableCards" :key="card.id" @click="toggleCardSelection(card)" :class="[
          'p-2 rounded cursor-pointer transition-all text-xs',
          selectedCards.find(c => c.id === card.id)
            ? 'bg-violet-600/50 border-violet-500 text-white'
            : 'bg-slate-700/30 border-white/5 hover:bg-slate-600/50 text-slate-300'
        ]">
          {{ card.label }}
        </div>
        <div v-if="availableCards.length === 0" class="col-span-2 text-center py-4 text-slate-400 text-xs">
          Нет карт на поле
        </div>
      </div>
    </div>

    <div class="flex gap-2">
      <button @click="selectDeckToAdd(editingDeck || { name: newDeckName })"
        class="px-3 py-2 bg-violet-600/50 hover:bg-violet-500 text-white rounded-lg transition-all"
        title="Создать на поле">
        <Layers class="w-4 h-4" />
      </button>
      <button @click="saveDeck" :disabled="!newDeckName.trim()"
        class="flex-1 px-4 py-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-all flex items-center justify-center gap-2 text-sm">
        <Save class="w-4 h-4" />
        Сохранить
      </button>
      <button @click="cancelEdit"
        class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-all text-sm">
        Отмена
      </button>
    </div>
  </div>
</template>