<script setup>
import { ref, computed, watch } from 'vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useGameWebSocket } from '@/composables/useGameWebSocket'
import {
  Search, LayoutGrid, Coins, Square, Box, Layers,
  Settings, Save, X, Upload, Plus, Trash2, Image as ImageIcon
} from 'lucide-vue-next'

const gameStore = useGameStore()
const userStore = useUserStore()
const { socket } = useGameWebSocket()

const searchQuery = ref('')
const selectedCategory = ref('all')
const editorObject = ref(null)
const showEditor = ref(false)
const editorTab = ref('basic')

const categories = [
  { id: 'all', label: 'Все', icon: LayoutGrid },
  { id: 'tokens', label: 'Токены', icon: Coins },
  { id: 'cards', label: 'Карты', icon: Square },
  { id: 'custom', label: '2D Объекты', icon: Box }
]

const objectTypes = [
  {
    id: 'dice',
    label: 'Кубик',
    icon: LayoutGrid,
    category: 'tokens',
    shape: 'square',
    defaults: { width: 60, height: 60, value: 1, diceSides: 6, label: 'd6' },
    editorFields: [
      { key: 'label', type: 'text', label: 'Название' },
      { key: 'width', type: 'number', label: 'Ширина', min: 20, max: 500 },
      { key: 'height', type: 'number', label: 'Высота', min: 20, max: 500 },
      { key: 'diceSides', type: 'number', label: 'Грани', min: 4, max: 100 },
      { key: 'value', type: 'number', label: 'Значение', min: 1 }
    ]
  },
  {
    id: 'card',
    label: 'Карта',
    icon: Square,
    category: 'cards',
    shape: 'square',
    defaults: { width: 120, height: 180, faceUp: true, cardData: { frontImage: null, backImage: null }, label: 'Новая карта' },
    editorFields: [
      { key: 'label', type: 'text', label: 'Название' },
      { key: 'width', type: 'number', label: 'Ширина', min: 20, max: 500 },
      { key: 'height', type: 'number', label: 'Высота', min: 20, max: 500 },
      { key: 'cardData.frontImage', type: 'image', label: 'Лицо' },
      { key: 'cardData.backImage', type: 'image', label: 'Рубашка' },
      { key: 'faceUp', type: 'checkbox', label: 'Лицом вверх' }
    ]
  },
  {
    id: 'deck',
    label: 'Колода',
    icon: Layers,
    category: 'cards',
    shape: 'square',
    defaults: { width: 120, height: 180, cards: [], cardCount: 0, label: 'Новая колода' },
    isDeck: true,
    editorFields: [
      { key: 'label', type: 'text', label: 'Название колоды' },
      { key: 'width', type: 'number', label: 'Ширина', min: 20, max: 500 },
      { key: 'height', type: 'number', label: 'Высота', min: 20, max: 500 }
    ]
  },
  {
    id: 'model2d',
    label: '2D Объект',
    icon: Box,
    category: 'custom',
    defaults: { width: 120, height: 120, url: null, label: 'Объект', rotation: 0, shape: 'square' },
    editorFields: [
      { key: 'label', type: 'text', label: 'Название' },
      { key: 'shape', type: 'select', label: 'Форма', options: ['square', 'circle', 'rounded'] },
      { key: 'width', type: 'number', label: 'Ширина', min: 20, max: 500 },
      { key: 'height', type: 'number', label: 'Высота', min: 20, max: 500 },
      { key: 'url', type: 'image', label: 'Изображение' },
      { key: 'rotation', type: 'range', label: 'Поворот', min: 0, max: 360, step: 15 }
    ]
  },
  {
    id: 'character',
    label: 'Токен персонажа',
    icon: Square,
    category: 'tokens',
    defaults: { width: 80, height: 80, characterImage: null, isEnemy: false, label: 'Герой', health: 100, shape: 'circle' },
    editorFields: [
      { key: 'label', type: 'text', label: 'Имя' },
      { key: 'shape', type: 'select', label: 'Форма', options: ['circle', 'square', 'rounded'] },
      { key: 'width', type: 'number', label: 'Ширина', min: 20, max: 500 },
      { key: 'height', type: 'number', label: 'Высота', min: 20, max: 500 },
      { key: 'characterImage', type: 'image', label: 'Аватар' },
      { key: 'isEnemy', type: 'checkbox', label: 'Противник' },
      { key: 'health', type: 'number', label: 'Здоровье', min: 0, default: 100 }
    ]
  },
  {
    id: 'counter',
    label: 'Счётчик',
    icon: Coins,
    category: 'tokens',
    defaults: { width: 50, height: 50, count: 1, label: 'Ресурс', color: '#f59e0b', shape: 'circle' },
    editorFields: [
      { key: 'label', type: 'text', label: 'Название' },
      { key: 'shape', type: 'select', label: 'Форма', options: ['circle', 'square', 'rounded'] },
      { key: 'width', type: 'number', label: 'Ширина', min: 20, max: 500 },
      { key: 'height', type: 'number', label: 'Высота', min: 20, max: 500 },
      { key: 'count', type: 'number', label: 'Количество', min: 0 },
      { key: 'color', type: 'color', label: 'Цвет' }
    ]
  }
]

const filteredTypes = computed(() => {
  let types = [...objectTypes]
  if (selectedCategory.value !== 'all') types = types.filter(t => t.category === selectedCategory.value)
  if (searchQuery.value) types = types.filter(t => t.label.toLowerCase().includes(searchQuery.value.toLowerCase()))
  return types
})

const objects = computed(() => {
  let filtered = gameStore.objects || []
  if (searchQuery.value) filtered = filtered.filter(obj => obj.label?.toLowerCase().includes(searchQuery.value.toLowerCase()))
  if (selectedCategory.value !== 'all') {
    const categoryTypes = objectTypes.filter(t => t.category === selectedCategory.value).map(t => t.id)
    filtered = filtered.filter(obj => categoryTypes.includes(obj.type))
  }
  return filtered
})

const openEditor = (typeConfig, existingObject = null) => {
  if (!typeConfig) return
  if (existingObject) {
    editorObject.value = { ...existingObject, editing: true }
  } else {
    editorObject.value = {
      id: `obj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: typeConfig.id,
      ...typeConfig.defaults,
      position: { x: 50000, y: 50000 },
      rotation: typeConfig.defaults?.rotation || 0,
      owner: userStore.userId,
      ownerId: userStore.userId,
      inHand: false,
      resizable: true,
      editing: false
    }
  }
  editorTab.value = 'basic'
  showEditor.value = true
}

const saveFromEditor = () => {
  if (!editorObject.value) return
  const obj = { ...editorObject.value }
  delete obj.editing

  if (obj.editing) {
    gameStore.updateObject(obj.id, obj)
    if (socket.value && gameStore.sessionId) {
      socket.value.emit('object:sync', {
        sessionId: gameStore.sessionId,
        userId: userStore.userId,
        update: { objectId: obj.id, changes: obj, type: 'editor-update' }
      })
    }
  } else {
    if (obj.type === 'deck') {
      gameStore.addDeck({ id: obj.id, name: obj.label, cards: obj.cards || [] }, obj.position)
    } else {
      gameStore.addObject(obj)
    }
    if (socket.value && gameStore.sessionId) {
      socket.value.emit('object:create', { sessionId: gameStore.sessionId, object: obj })
    }
  }
  showEditor.value = false
  editorObject.value = null
}

const triggerImageUpload = (field) => {
  const input = document.getElementById(`imgInput_${field}`)
  if (input) input.click()
}

const handleImageUpload = (field, event) => {
  const file = event.target.files[0]
  if (!file || !editorObject.value) return
  if (file.size > 2 * 1024 * 1024) { alert('Файл слишком большой. Максимум 2MB.'); return }

  const reader = new FileReader()
  reader.onload = (e) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.')
      if (!editorObject.value[parent]) editorObject.value[parent] = {}
      editorObject.value[parent][child] = e.target.result
    } else {
      editorObject.value[field] = e.target.result
    }
  }
  reader.onerror = () => alert('Ошибка загрузки изображения')
  reader.readAsDataURL(file)
}

const getImageValue = (field) => {
  if (field.includes('.')) {
    const [parent, child] = field.split('.')
    return editorObject.value[parent]?.[child] || null
  }
  return editorObject.value[field] || null
}

const clearImage = (field) => {
  if (field.includes('.')) {
    const [parent, child] = field.split('.')
    if (editorObject.value[parent]) editorObject.value[parent][child] = null
  } else {
    editorObject.value[field] = null
  }
}

const deleteObject = (objectId) => {
  if (!confirm('Удалить объект?')) return
  const obj = gameStore.objects.find(o => o.id === objectId)
  if (obj?.type === 'deck') gameStore.removeDeck(objectId)
  else gameStore.removeObject(objectId)
  if (socket.value && gameStore.sessionId) socket.value.emit('object:delete', { sessionId: gameStore.sessionId, objectId })
}

const quickCreate = (typeId, extraProps = {}) => {
  const typeConfig = objectTypes.find(t => t.id === typeId)
  if (!typeConfig) return
  openEditor(typeConfig)
  if (editorObject.value) {
    Object.assign(editorObject.value, extraProps)
    saveFromEditor()
  }
}

watch(() => showEditor.value, (val) => {
  if (val) {
    const onKey = (e) => { if (e.key === 'Escape') showEditor.value = false }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }
})
</script>

<template>
  <div class="space-y-4 p-3">
    <div class="space-y-3">
      <div class="relative">
        <input v-model="searchQuery" type="text" placeholder="Поиск объектов..."
          class="w-full px-4 py-2.5 pl-10 bg-slate-800/60 border border-white/10 rounded-xl text-sm text-white placeholder-slate-400 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all" />
        <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
      </div>
      <div class="flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
        <button v-for="cat in categories" :key="cat.id" @click="selectedCategory = cat.id"
          :class="['px-3.5 py-2 rounded-xl text-xs font-medium flex items-center gap-2 whitespace-nowrap transition-all duration-200', selectedCategory === cat.id ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/25' : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700 hover:text-white border border-white/5']">
          <component :is="cat.icon" class="w-4 h-4" /> {{ cat.label }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-3 gap-2.5">
      <button v-for="type in filteredTypes" :key="type.id" @click="openEditor(type)"
        class="p-3.5 bg-slate-800/60 hover:bg-slate-700 border border-white/5 hover:border-violet-500/50 rounded-xl transition-all duration-200 flex flex-col items-center gap-2.5 group hover:shadow-lg hover:shadow-violet-500/10 hover:-translate-y-0.5"
        :title="type.label">
        <div class="relative">
          <component :is="type.icon"
            class="w-5 h-5 text-violet-400 group-hover:text-violet-300 transition-colors duration-200" />
          <div
            class="absolute inset-0 blur-lg bg-violet-500/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          </div>
        </div>
        <span
          class="text-[11px] font-medium text-slate-300 group-hover:text-white text-center leading-tight transition-colors">{{
            type.label }}</span>
        <Settings
          class="w-3.5 h-3.5 text-slate-500 opacity-0 group-hover:opacity-100 transition-all duration-200 group-hover:text-violet-400" />
      </button>
    </div>

    <div class="border-t border-white/10 pt-3.5">
      <h4 class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-2">
        <Layers class="w-3.5 h-3.5" /> Объекты на поле
      </h4>
      <div class="max-h-44 overflow-y-auto space-y-2 pr-1 scrollbar-thin">
        <div v-for="obj in objects" :key="obj.id"
          class="p-2.5 bg-slate-800/40 border border-white/5 rounded-xl flex items-center justify-between hover:bg-slate-800/60 hover:border-violet-500/20 transition-all duration-200 group">
          <div class="min-w-0 cursor-pointer flex-1" @click="openEditor(objectTypes.find(t => t.id === obj.type), obj)">
            <h4 class="text-sm font-medium text-white truncate group-hover:text-violet-300 transition-colors">{{
              obj.label }}</h4>
            <p class="text-[10px] text-slate-400 mt-0.5">
              {{ obj.type }} • {{ obj.width }}×{{ obj.height }}
              <span v-if="obj.type === 'dice'" class="text-cyan-400">• d{{ obj.diceSides || 6 }}</span>
              <span v-if="obj.type === 'counter'" class="text-amber-400">• ×{{ obj.count || 1 }}</span>
              <span v-if="obj.type === 'deck'" class="text-violet-400">• {{ obj.cardCount || 0 }} карт</span>
            </p>
          </div>
          <div class="flex gap-1.5 ml-2">
            <button @click="openEditor(objectTypes.find(t => t.id === obj.type), obj)"
              class="p-1.5 bg-violet-600/20 hover:bg-violet-500/30 text-violet-300 hover:text-violet-200 rounded-lg transition-all flex-shrink-0"
              title="Редактировать">
              <Settings class="w-3.5 h-3.5" />
            </button>
            <button @click="deleteObject(obj.id)"
              class="p-1.5 bg-red-600/20 hover:bg-red-500/30 text-red-300 hover:text-red-200 rounded-lg transition-all flex-shrink-0"
              title="Удалить">
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        <div v-if="objects.length === 0" class="text-center py-8 text-slate-500">
          <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-800/50 flex items-center justify-center">
            <Box class="w-6 h-6 opacity-50" />
          </div>
          <p class="text-sm font-medium">Нет объектов</p>
          <p class="text-[11px] mt-1 text-slate-400">Создайте первый объект выше</p>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showEditor && editorObject"
        class="fixed inset-0 z-[200] flex items-center justify-center bg-black/70 backdrop-blur-md p-4"
        @click.self="showEditor = false">
        <div
          class="bg-slate-900 border border-white/10 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-scale-in">
          <div
            class="p-4 border-b border-white/10 flex justify-between items-center bg-gradient-to-r from-slate-800/50 to-transparent">
            <h3 class="text-lg font-bold text-white flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-xl bg-violet-500/20 flex items-center justify-center">
                <Settings class="w-4 h-4 text-violet-400" />
              </div>
              {{ editorObject.editing ? 'Редактировать' : 'Создать' }}: {{ editorObject.label }}
            </h3>
            <button @click="showEditor = false"
              class="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="flex border-b border-white/10 bg-slate-800/30">
            <button @click="editorTab = 'basic'"
              :class="['flex-1 py-3 text-sm font-medium transition-all duration-200', editorTab === 'basic' ? 'text-violet-400 border-b-2 border-violet-400 bg-violet-500/5' : 'text-slate-400 hover:text-slate-300 hover:bg-white/5']">Основные</button>
            <button @click="editorTab = 'appearance'"
              :class="['flex-1 py-3 text-sm font-medium transition-all duration-200', editorTab === 'appearance' ? 'text-violet-400 border-b-2 border-violet-400 bg-violet-500/5' : 'text-slate-400 hover:text-slate-300 hover:bg-white/5']">Внешний
              вид</button>
            <button v-if="editorObject.type === 'card' || editorObject.type === 'model2d'" @click="editorTab = 'images'"
              :class="['flex-1 py-3 text-sm font-medium transition-all duration-200', editorTab === 'images' ? 'text-violet-400 border-b-2 border-violet-400 bg-violet-500/5' : 'text-slate-400 hover:text-slate-300 hover:bg-white/5']">Изображения</button>
          </div>

          <div class="p-4 max-h-[55vh] overflow-y-auto space-y-4 scrollbar-thin">
            <template v-if="editorTab === 'basic'">
              <div
                v-for="field in objectTypes.find(t => t.id === editorObject.type)?.editorFields?.filter(f => f.type !== 'image' && f.type !== 'color')"
                :key="field.key" class="space-y-2">
                <label class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{{ field.label
                  }}</label>
                <input v-if="field.type === 'text'" v-model="editorObject[field.key]" type="text"
                  class="w-full px-3.5 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all" />
                <input v-else-if="field.type === 'number'" v-model.number="editorObject[field.key]" type="number"
                  :min="field.min" :max="field.max" :step="field.step || 1"
                  class="w-full px-3.5 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all" />
                <input v-else-if="field.type === 'range'" v-model.number="editorObject[field.key]" type="range"
                  :min="field.min" :max="field.max" :step="field.step || 1"
                  class="w-full accent-violet-500 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer" />
                <label v-else-if="field.type === 'checkbox'" class="flex items-center gap-3 cursor-pointer group">
                  <input v-model="editorObject[field.key]" type="checkbox"
                    class="w-4.5 h-4.5 rounded bg-slate-800 border-white/10 accent-violet-500 cursor-pointer" />
                  <span class="text-sm text-slate-300 group-hover:text-white transition-colors">{{ field.label }}</span>
                </label>
                <select v-else-if="field.type === 'select'" v-model="editorObject[field.key]"
                  class="w-full px-3.5 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all">
                  <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </div>
            </template>

            <template v-if="editorTab === 'appearance'">
              <div class="space-y-2">
                <label class="text-[11px] font-semibold text-slate-400 uppercase">Поворот: {{ editorObject.rotation
                  }}°</label>
                <input v-model.number="editorObject.rotation" type="range" min="0" max="360" step="15"
                  class="w-full accent-violet-500 h-2 bg-slate-700 rounded-lg" />
                <div class="flex gap-2">
                  <button @click="editorObject.rotation = (editorObject.rotation - 90 + 360) % 360"
                    class="flex-1 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs text-slate-300 hover:text-white transition-all">−90°</button>
                  <button @click="editorObject.rotation = (editorObject.rotation + 90) % 360"
                    class="flex-1 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs text-slate-300 hover:text-white transition-all">+90°</button>
                </div>
              </div>
              <div v-if="editorObject.type === 'dice'"
                class="p-3 bg-slate-800/50 rounded-xl border border-white/5 mt-4">
                <label class="text-[11px] font-semibold text-slate-400 uppercase mb-2.5 block">Предпросмотр</label>
                <div class="text-5xl text-center text-cyan-400 drop-shadow-lg">{{ ['⚀', '⚁', '⚂', '', '⚄',
                  '⚅'][editorObject.value - 1] || '🎲' }}</div>
              </div>
              <div v-if="editorObject.type === 'counter'" class="space-y-2 mt-4">
                <label class="text-[11px] font-semibold text-slate-400 uppercase">Цвет</label>
                <div class="flex items-center gap-3">
                  <input v-model="editorObject.color" type="color"
                    class="w-12 h-12 rounded-xl cursor-pointer border-2 border-white/10 bg-slate-800" />
                  <span class="text-sm text-slate-300 font-mono">{{ editorObject.color || '#f59e0b' }}</span>
                </div>
              </div>
            </template>

            <template v-if="editorTab === 'images'">
              <div
                v-for="field in objectTypes.find(t => t.id === editorObject.type)?.editorFields?.filter(f => f.type === 'image')"
                :key="field.key" class="space-y-2">
                <label class="text-[11px] font-semibold text-slate-400 uppercase">{{ field.label }}</label>
                <div
                  class="border-2 border-dashed border-white/10 rounded-xl p-4 text-center hover:border-violet-500/50 transition-colors cursor-pointer bg-slate-800/30 hover:bg-slate-800/50"
                  @click="triggerImageUpload(field.key)">
                  <img v-if="getImageValue(field.key)" :src="getImageValue(field.key)"
                    class="max-h-32 mx-auto rounded-lg object-contain shadow-lg" />
                  <div v-else class="text-slate-500 text-sm flex flex-col items-center gap-2">
                    <div class="w-10 h-10 rounded-xl bg-slate-700/50 flex items-center justify-center">
                      <Upload class="w-5 h-5 opacity-50" />
                    </div>
                    <span>Нажмите для загрузки</span>
                    <span class="text-[10px] text-slate-400">PNG, JPG до 2MB</span>
                  </div>
                  <input :id="`imgInput_${field.key}`" type="file" accept="image/*" class="hidden"
                    @change="handleImageUpload(field.key, $event)" />
                </div>
                <button v-if="getImageValue(field.key)" @click="clearImage(field.key)"
                  class="w-full py-2 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-all">Удалить
                  изображение</button>
              </div>
            </template>
          </div>

          <div class="p-4 border-t border-white/10 bg-slate-800/30 flex gap-3">
            <button @click="showEditor = false"
              class="flex-1 py-2.5 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-medium transition-all">Отмена</button>
            <button @click="saveFromEditor"
              class="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-medium flex items-center justify-center gap-2 transition-all shadow-lg shadow-violet-500/25">
              <Save class="w-4 h-4" /> {{ editorObject.editing ? 'Сохранить' : 'Создать' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scale-in {
  animation: scale-in 0.2s ease-out;
}

.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(71, 85, 105, 0.5);
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgba(71, 85, 105, 0.7);
}
</style>