<script setup>
import { ref, onMounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useGameWebSocket } from '@/composables/useGameWebSocket'
import axios from 'axios'
import {
  Gamepad2, Save, Trash2, RotateCcw, Download, Loader2,
  CheckCircle2, AlertCircle, X, FileJson, Trash
} from 'lucide-vue-next'

const gameStore = useGameStore()
const userStore = useUserStore()
const { socket } = useGameWebSocket()

const templateName = ref('')
const description = ref('')
const isSaving = ref(false)
const isLoading = ref(false)
const savedTemplates = ref([])
const confirmClear = ref(false)
const confirmDelete = ref(null)
const notification = ref({ show: false, type: 'success', message: '' })

// 🔧 Явно указываем полный URL бэкенда, чтобы избежать 404 при разных портах
const API_BASE = 'http://localhost:5000/api/game'
const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const showNotification = (type, message) => {
  notification.value = { show: true, type, message }
  setTimeout(() => { notification.value.show = false }, 3000)
}

const fetchTemplates = async () => {
  try {
    isLoading.value = true
    console.log('📡 Fetching templates from:', `${API_BASE}/templates`)
    const { data } = await api.get('/templates')
    savedTemplates.value = data.templates || []
  } catch (err) {
    console.warn('Failed to fetch templates:', err.response?.status, err.response?.data || err.message)
    savedTemplates.value = []
  } finally {
    isLoading.value = false
  }
}

const saveTemplate = async () => {
  if (!templateName.value.trim()) {
    showNotification('error', 'Введите название шаблона')
    return
  }
  if (!gameStore.objects.length && !gameStore.drawings.length) {
    showNotification('error', 'Поле пусто. Нечего сохранять.')
    return
  }

  try {
    isSaving.value = true
    const payload = {
      name: templateName.value.trim(),
      description: description.value.trim(),
      state: {
        objects: gameStore.objects,
        drawings: gameStore.drawings,
        decks: gameStore.decks,
        settings: gameStore.settings
      }
    }

    console.log('💾 Saving to:', `${API_BASE}/templates`)
    console.log('📦 Payload:', payload)

    const response = await api.post('/templates', payload)
    console.log('✅ Response:', response.data)

    showNotification('success', 'Шаблон успешно сохранён!')
    templateName.value = ''
    description.value = ''
    await fetchTemplates()
  } catch (err) {
    console.error('❌ Save failed:', err.response?.status, err.response?.data || err.message)
    showNotification('error', `Ошибка ${err.response?.status || ''}: ${err.response?.data?.error || 'Проверьте консоль'}`)
  } finally {
    isSaving.value = false
  }
}

const loadTemplate = async (template) => {
  if (!confirm(`Загрузить шаблон "${template.name}"? Текущее поле будет заменено.`)) return

  try {
    isLoading.value = true
    const state = template.state

    gameStore.objects = state.objects || []
    gameStore.drawings = state.drawings || []
    gameStore.decks = state.decks || []
    if (state.settings) gameStore.settings = { ...gameStore.settings, ...state.settings }

    gameStore.debouncedSave(true)

    if (socket.value && gameStore.sessionId) {
      socket.value.emit('object:sync', {
        sessionId: gameStore.sessionId,
        userId: userStore.userId,
        update: { type: 'board-reset', state }
      })
    }

    showNotification('success', 'Шаблон загружен на поле')
  } catch (err) {
    console.error('Load failed:', err)
    showNotification('error', 'Ошибка загрузки шаблона')
  } finally {
    isLoading.value = false
  }
}

const deleteTemplate = async (template) => {
  try {
    await api.delete(`/templates/${template.id}`)
    showNotification('success', 'Шаблон удалён')
    await fetchTemplates()
    confirmDelete.value = null
  } catch (err) {
    console.error('Delete failed:', err.response?.status, err.response?.data || err.message)
    showNotification('error', 'Не удалось удалить шаблон')
  }
}

const clearBoard = async () => {
  if (!confirmClear.value) {
    confirmClear.value = true
    setTimeout(() => { confirmClear.value = false }, 3000)
    return
  }

  try {
    gameStore.objects = []
    gameStore.drawings = []
    gameStore.decks = []

    gameStore.debouncedSave(true)

    if (socket.value && gameStore.sessionId) {
      socket.value.emit('object:sync', {
        sessionId: gameStore.sessionId,
        userId: userStore.userId,
        update: { type: 'board-clear' }
      })
    }

    showNotification('success', 'Поле полностью очищено')
    confirmClear.value = false
  } catch (err) {
    console.error('Clear failed:', err)
    showNotification('error', 'Ошибка очистки поля')
  }
}

onMounted(() => {
  fetchTemplates()
})
</script>

<template>
  <div class="space-y-5">
    <!-- Уведомления -->
    <Transition name="fade-slide">
      <div v-if="notification.show"
        class="fixed top-6 right-6 z-[300] px-4 py-3 rounded-xl shadow-2xl border backdrop-blur-md flex items-center gap-3 min-w-[280px]"
        :class="notification.type === 'success'
          ? 'bg-emerald-900/80 border-emerald-500/30 text-emerald-200'
          : 'bg-red-900/80 border-red-500/30 text-red-200'">
        <component :is="notification.type === 'success' ? CheckCircle2 : AlertCircle" class="w-5 h-5 flex-shrink-0" />
        <span class="text-sm font-medium">{{ notification.message }}</span>
        <button @click="notification.show = false" class="ml-auto opacity-60 hover:opacity-100">
          <X class="w-4 h-4" />
        </button>
      </div>
    </Transition>

    <!-- Заголовок -->
    <div class="text-center py-4">
      <div
        class="w-14 h-14 mx-auto mb-3 rounded-2xl bg-violet-500/10 flex items-center justify-center border border-violet-500/20">
        <Gamepad2 class="w-7 h-7 text-violet-400" />
      </div>
      <h3 class="text-lg font-bold text-white mb-1">Управление полем</h3>
      <p class="text-sm text-slate-400">Сохраняйте, загружайте и очищайте расстановку</p>
    </div>

    <!-- Форма сохранения -->
    <div class="space-y-3 bg-slate-800/40 p-4 rounded-2xl border border-white/5">
      <div class="flex items-center gap-2 mb-2">
        <Save class="w-4 h-4 text-violet-400" />
        <span class="text-sm font-semibold text-white">Сохранить текущее поле</span>
      </div>
      <input v-model="templateName" type="text" placeholder="Название шаблона" maxlength="40"
        class="w-full px-3.5 py-2.5 bg-slate-900/60 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all" />
      <textarea v-model="description" placeholder="Описание (необязательно)" rows="2" maxlength="150"
        class="w-full px-3.5 py-2.5 bg-slate-900/60 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all resize-none" />
      <button @click="saveTemplate" :disabled="isSaving || !templateName.trim()"
        class="w-full px-4 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all flex items-center justify-center gap-2 shadow-lg shadow-violet-500/20">
        <Loader2 v-if="isSaving" class="w-4 h-4 animate-spin" />
        <Save v-else class="w-4 h-4" />
        {{ isSaving ? 'Сохранение...' : 'Сохранить шаблон' }}
      </button>
    </div>

    <!-- Очистка поля -->
    <div class="bg-slate-800/40 p-4 rounded-2xl border border-white/5">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <RotateCcw class="w-4 h-4 text-amber-400" />
          <span class="text-sm font-semibold text-white">Очистить поле</span>
        </div>
        <span class="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20">
          {{ gameStore.objects.length + gameStore.drawings.length }} объектов
        </span>
      </div>
      <button @click="clearBoard" :class="[
        'w-full px-4 py-2.5 rounded-xl font-medium transition-all flex items-center justify-center gap-2 border',
        confirmClear
          ? 'bg-red-600 border-red-500 text-white hover:bg-red-500 shadow-lg shadow-red-500/20'
          : 'bg-slate-700/50 border-white/5 text-slate-300 hover:bg-red-900/30 hover:border-red-500/30 hover:text-red-300'
      ]">
        <Trash2 class="w-4 h-4" />
        {{ confirmClear ? 'Нажмите ещё раз для подтверждения' : 'Очистить всё' }}
      </button>
      <p v-if="confirmClear" class="text-[10px] text-slate-400 mt-2 text-center">Действие необратимо и синхронизируется
        со всеми игроками</p>
    </div>

    <!-- Список шаблонов -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <h4 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Сохранённые шаблоны</h4>
        <button @click="fetchTemplates" :disabled="isLoading"
          class="text-[10px] text-violet-400 hover:text-violet-300 disabled:opacity-50">
          Обновить
        </button>
      </div>

      <div v-if="isLoading" class="flex justify-center py-6">
        <Loader2 class="w-6 h-6 text-violet-400 animate-spin" />
      </div>

      <div v-else-if="savedTemplates.length === 0"
        class="text-center py-6 bg-slate-800/30 rounded-xl border border-dashed border-white/10">
        <FileJson class="w-8 h-8 mx-auto mb-2 text-slate-600" />
        <p class="text-sm text-slate-400">Нет сохранённых шаблонов</p>
      </div>

      <div v-else class="space-y-2 max-h-48 overflow-y-auto pr-1 scrollbar-thin">
        <div v-for="tpl in savedTemplates" :key="tpl.id"
          class="group p-3 bg-slate-800/50 border border-white/5 rounded-xl hover:border-violet-500/30 hover:bg-slate-800/70 transition-all">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0 flex-1 cursor-pointer" @click="loadTemplate(tpl)">
              <h5 class="text-sm font-medium text-white truncate group-hover:text-violet-300 transition-colors">{{
                tpl.name }}</h5>
              <p v-if="tpl.description" class="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{{ tpl.description }}</p>
              <div class="flex items-center gap-3 mt-1.5">
                <span class="text-[9px] text-slate-500">{{ new Date(tpl.createdAt).toLocaleDateString() }}</span>
                <span class="text-[9px] px-1.5 py-0.5 rounded bg-slate-700/50 text-slate-400">
                  {{ tpl.state?.objects?.length || 0 }} объектов
                </span>
              </div>
            </div>
            <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click.stop="loadTemplate(tpl)"
                class="p-1.5 rounded-lg bg-violet-500/20 hover:bg-violet-500/30 text-violet-300 transition-colors"
                title="Загрузить">
                <Download class="w-3.5 h-3.5" />
              </button>
              <button @click.stop="confirmDelete = tpl"
                class="p-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors"
                title="Удалить">
                <Trash class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка удаления -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="confirmDelete"
          class="fixed inset-0 z-[250] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          @click.self="confirmDelete = null">
          <div class="bg-slate-900 border border-white/10 rounded-2xl p-5 max-w-sm w-full shadow-2xl">
            <h4 class="text-base font-bold text-white mb-2">Удалить шаблон?</h4>
            <p class="text-sm text-slate-400 mb-4">"{{ confirmDelete.name }}" будет удалён безвозвратно.</p>
            <div class="flex gap-3">
              <button @click="confirmDelete = null"
                class="flex-1 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-xl text-sm font-medium transition-all">Отмена</button>
              <button @click="deleteTemplate(confirmDelete)"
                class="flex-1 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-sm font-medium transition-all flex items-center justify-center gap-2">
                <Trash2 class="w-4 h-4" /> Удалить
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.4);
  border-radius: 2px;
}
</style>