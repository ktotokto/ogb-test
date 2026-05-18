<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useGameStore } from '@/stores/game'
import { Gamepad2, Plus, Edit2, Trash2, LogOut, Settings, Users, Lock, Unlock, X, Save } from 'lucide-vue-next'
import axios from 'axios'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const savedGames = ref([])
const isLoading = ref(false)
const isCreating = ref(false)
const editingSession = ref(null)

const sessionForm = ref({
  name: '',
  maxPlayers: 8,
  isPrivate: false
})

const fetchSavedGames = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('/api/game/sessions', {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    savedGames.value = response.data.sessions || []
  } catch (err) {
    console.error('Failed to fetch games:', err)
    savedGames.value = []
  } finally {
    isLoading.value = false
  }
}

const startCreate = () => {
  editingSession.value = null
  sessionForm.value = { name: '', maxPlayers: 8, isPrivate: false }
  isCreating.value = true
}

const startEdit = (session) => {
  editingSession.value = session
  sessionForm.value = {
    name: session.name || '',
    maxPlayers: session.max_players || 8,
    isPrivate: session.is_private || false
  }
  isCreating.value = true
}

const cancelEdit = () => {
  isCreating.value = false
  editingSession.value = null
}

const saveSession = async () => {
  if (!sessionForm.value.name.trim()) return

  isLoading.value = true
  try {
    const token = userStore.token

    if (editingSession.value) {
      await axios.put(
        `/api/game/session/${editingSession.value.id}`,
        {
          name: sessionForm.value.name,
          max_players: sessionForm.value.maxPlayers,
          is_private: sessionForm.value.isPrivate
        },
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
    } else {
      const response = await axios.post(
        '/api/game/session/create',
        {
          name: sessionForm.value.name,
          isPrivate: sessionForm.value.isPrivate,
          maxPlayers: sessionForm.value.maxPlayers
        },
        { headers: { 'Authorization': `Bearer ${token}` } }
      )

      if (response.data.session) {
        savedGames.value.push(response.data.session)
      }
    }

    await fetchSavedGames()
    cancelEdit()
  } catch (err) {
    console.error('Failed to save session:', err)
    alert('Ошибка: ' + (err.response?.data?.error || err.message))
  } finally {
    isLoading.value = false
  }
}

const deleteSession = async (sessionId) => {
  if (!confirm('Удалить эту игру?')) return

  try {
    await axios.delete(`/api/game/session/${sessionId}`, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    await fetchSavedGames()
  } catch (err) {
    console.error('Failed to delete session:', err)
    alert('Ошибка: ' + (err.response?.data?.error || err.message))
  }
}

const joinSession = async (session) => {
  try {
    const token = userStore.token

    // Join via API
    await axios.post(
      '/api/game/session/join',
      { sessionId: session.id },
      { headers: { 'Authorization': `Bearer ${token}` } }
    )

    // Navigate to game
    router.push(`/game/${session.id}`)
  } catch (err) {
    console.error('Failed to join session:', err)
    alert('Ошибка: ' + (err.response?.data?.error || err.message))
  }
}

onMounted(async () => {
  await fetchSavedGames()
})
</script>

<template>
  <div class="min-h-screen bg-slate-950 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-white mb-8 flex items-center gap-3">
        <Settings class="w-7 h-7 text-violet-400" />
        Мои игры
      </h1>

      <div v-if="isCreating" class="bg-slate-900/80 backdrop-blur rounded-2xl border border-white/10 p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-white">
            {{ editingSession ? 'Редактировать игру' : 'Новая игра' }}
          </h2>
          <button @click="cancelEdit" class="text-slate-400 hover:text-white transition-colors">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">Название игры</label>
            <input v-model="sessionForm.name" type="text" placeholder="Введите название..."
              class="w-full px-4 py-3 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-violet-500" />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">
              Максимум игроков: {{ sessionForm.maxPlayers }}
            </label>
            <input v-model="sessionForm.maxPlayers" type="range" min="2" max="16" class="w-full accent-violet-500" />
          </div>

          <div class="flex items-center gap-3">
            <input v-model="sessionForm.isPrivate" type="checkbox" id="isPrivate"
              class="w-4 h-4 rounded bg-slate-800 border-white/10 accent-violet-500" />
            <label for="isPrivate" class="text-sm text-slate-300 flex items-center gap-2">
              <component :is="sessionForm.isPrivate ? Lock : Unlock" class="w-4 h-4" />
              Приватная игра
            </label>
          </div>

          <div class="flex gap-3 pt-2">
            <button @click="saveSession" :disabled="isLoading || !sessionForm.name.trim()"
              class="flex-1 py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-medium flex items-center justify-center gap-2 transition-colors">
              <Save class="w-4 h-4" />
              {{ isLoading ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button @click="cancelEdit"
              class="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-medium transition-colors">
              Отмена
            </button>
          </div>
        </div>
      </div>

      <div v-else class="bg-slate-900/80 backdrop-blur rounded-2xl border border-white/10 p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-white flex items-center gap-2">
            <Gamepad2 class="w-5 h-5 text-emerald-400" />
            Активные сессии
          </h2>
          <button @click="startCreate"
            class="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-xl text-sm font-medium flex items-center gap-2 transition-colors">
            <Plus class="w-4 h-4" />
            Создать игру
          </button>
        </div>

        <div v-if="isLoading && !savedGames.length" class="text-center text-slate-500 py-12">
          Загрузка...
        </div>

        <div v-else-if="!savedGames || savedGames.length === 0" class="text-center text-slate-500 py-12">
          <Gamepad2 class="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p class="text-lg">У вас нет активных игр</p>
          <p class="text-sm mt-1">Создайте первую игру, чтобы начать</p>
        </div>

        <div v-else class="space-y-3">
          <div v-for="game in savedGames" :key="game.id"
            class="p-4 bg-slate-800/30 rounded-xl hover:bg-slate-800/50 transition-colors border border-white/5">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <h3 class="text-white font-semibold truncate">{{ game.name }}</h3>
                  <span v-if="game.is_private"
                    class="px-2 py-0.5 bg-amber-500/20 text-amber-400 text-xs rounded-full flex items-center gap-1">
                    <Lock class="w-3 h-3" />
                    Приватная
                  </span>
                </div>
                <div class="flex items-center gap-4 text-sm text-slate-400">
                  <span class="flex items-center gap-1">
                    <Users class="w-4 h-4" />
                    {{ game.players?.length || 0 }} / {{ game.max_players }}
                  </span>
                  <span>•</span>
                  <span>{{ new Date(game.created_at).toLocaleDateString('ru-RU') }}</span>
                </div>
              </div>

              <div class="flex items-center gap-2 flex-shrink-0">
                <button @click="startEdit(game)"
                  class="p-2 hover:bg-slate-700 text-slate-400 hover:text-white rounded-lg transition-colors"
                  title="Редактировать">
                  <Edit2 class="w-4 h-4" />
                </button>
                <button @click="deleteSession(game.id)"
                  class="p-2 hover:bg-red-600/20 text-slate-400 hover:text-red-400 rounded-lg transition-colors"
                  title="Удалить">
                  <Trash2 class="w-4 h-4" />
                </button>
                <button @click="joinSession(game)"
                  class="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white text-sm rounded-lg font-medium flex items-center gap-2 transition-colors">
                  <LogOut class="w-4 h-4" />
                  Играть
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>