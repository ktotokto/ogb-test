<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useGameStore } from '@/stores/game'
import { UserPlus, UserCheck, UserX, Search, Gamepad2, Save, Share2 } from 'lucide-vue-next'
import axios from 'axios'

const userStore = useUserStore()
const gameStore = useGameStore()

const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const savedGames = ref([])
const isLoading = ref(false)
const searchError = ref(null) 

const friendsList = computed(() => userStore.friends || [])
const requests = computed(() => userStore.friendRequests || [])

const searchUsers = async () => {
  if (searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  
  isSearching.value = true
  searchError.value = null
  
  try {
    const response = await axios.get('/api/users/search', {
      params: { query: searchQuery.value },                
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    searchResults.value = response.data || []
    
    if (searchResults.value.length === 0) {
      searchError.value = 'Пользователи не найдены'
    }
  } catch (err) {
    console.error('Search failed:', err)
    searchError.value = err.response?.data?.error || 'Ошибка поиска'
    
    if (err.response?.status === 401) {
      userStore.logout()
      router.push('/login')
    }
  } finally {
    isSearching.value = false
  }
}

const sendFriendRequest = async (userId) => {
  try {
    await axios.post('/api/friends/request', { receiverId: userId })
    searchResults.value = searchResults.value.filter(u => u.id !== userId)
  } catch (err) {
    console.error('Failed to send request:', err)
  }
}

const acceptFriendRequest = async (friendshipId) => {
  try {
    await axios.post(`/api/friends/accept/${friendshipId}`)
    await userStore.fetchFriends?.()
  } catch (err) {
    console.error('Failed to accept:', err)
  }
}

const declineFriendRequest = async (friendshipId) => {
  try {
    await axios.post(`/api/friends/decline/${friendshipId}`)
    // Удаляем из локального списка
    const idx = requests.value.findIndex(r => r.friendship?.id === friendshipId)
    if (idx !== -1) {
      requests.value.splice(idx, 1)
    }
  } catch (err) {
    console.error('Failed to decline:', err)
  }
}

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

const inviteFriend = async (friendId, sessionId) => {
  if (!sessionId) {
    alert('Сначала создайте или откройте игру')
    return
  }
  try {
    await axios.post('/api/game/session/invite', {
      sessionId,
      receiverId: friendId
    })
    alert('Приглашение отправлено!')
  } catch (err) {
    console.error('Failed to invite:', err)
    alert('Ошибка при отправке приглашения')
  }
}

onMounted(async () => {
  // ✅ Инициализация данных
  await userStore.fetchProfile?.()
  await userStore.fetchFriends?.()
  await userStore.fetchFriendRequests?.()
  await fetchSavedGames()
})
</script>

<template>
  <div class="min-h-screen bg-slate-950 py-8">
    <div class="max-w-6xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-white mb-8">Друзья и Игры</h1>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Поиск друзей -->
        <div class="bg-slate-900/80 backdrop-blur rounded-2xl border border-white/10 p-6">
          <h2 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Search class="w-5 h-5 text-violet-400" />
            Поиск друзей
          </h2>
          
          <div class="relative mb-4">
            <input
              v-model="searchQuery"
              @input="searchUsers"
              type="text"
              placeholder="Введите имя пользователя..."
              class="w-full px-4 py-3 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-violet-500"
            />
          </div>

          <div class="space-y-2 max-h-64 overflow-y-auto">
            <div v-for="user in searchResults" :key="user.id" class="flex items-center justify-between p-3 bg-slate-800/30 rounded-xl">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center">
                  <span class="text-white font-bold">{{ user.username?.[0]?.toUpperCase() || '?' }}</span>
                </div>
                <div>
                  <p class="text-white font-medium">{{ user.username }}</p>
                  <p class="text-xs text-slate-400">{{ user.email }}</p>
                </div>
              </div>
              <button
                @click="sendFriendRequest(user.id)"
                class="p-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg transition-colors"
              >
                <UserPlus class="w-4 h-4" />
              </button>
            </div>
            <p v-if="isSearching" class="text-center text-slate-500 py-4">Поиск...</p>
            <p v-if="!isSearching && searchResults.length === 0 && searchQuery.length >= 2" class="text-center text-slate-500 py-4">
              Ничего не найдено
            </p>
          </div>
        </div>

        <!-- Запросы в друзья -->
        <div class="bg-slate-900/80 backdrop-blur rounded-2xl border border-white/10 p-6">
          <h2 class="text-xl font-bold text-white mb-4">Запросы в друзья</h2>
          
          <div v-if="!requests || requests.length === 0" class="text-center text-slate-500 py-8">
            Нет новых запросов
          </div>
          
          <div v-else class="space-y-2">
            <div v-for="req in requests" :key="req.friendship?.id || req.id" class="flex items-center justify-between p-3 bg-slate-800/30 rounded-xl">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
                  <span class="text-white font-bold">{{ req.requester?.username?.[0]?.toUpperCase() || '?' }}</span>
                </div>
                <span class="text-white font-medium">{{ req.requester?.username || 'Unknown' }}</span>
              </div>
              <div class="flex gap-2">
                <button @click="acceptFriendRequest(req.friendship?.id)" class="p-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg">
                  <UserCheck class="w-4 h-4" />
                </button>
                <button @click="declineFriendRequest(req.friendship?.id)" class="p-2 bg-red-600 hover:bg-red-500 text-white rounded-lg">
                  <UserX class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Список друзей -->
        <div class="bg-slate-900/80 backdrop-blur rounded-2xl border border-white/10 p-6">
          <h2 class="text-xl font-bold text-white mb-4">Мои друзья</h2>
          
          <div v-if="!friendsList || friendsList.length === 0" class="text-center text-slate-500 py-8">
            У вас пока нет друзей
          </div>
          
          <div v-else class="space-y-2">
            <div v-for="friend in friendsList" :key="friend.id" class="flex items-center justify-between p-3 bg-slate-800/30 rounded-xl">
              <div class="flex items-center gap-3">
                <div class="relative">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center">
                    <span class="text-white font-bold">{{ friend.username?.[0]?.toUpperCase() || '?' }}</span>
                  </div>
                  <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-slate-900" :class="friend.is_online ? 'bg-emerald-400' : 'bg-slate-500'" />
                </div>
                <div>
                  <p class="text-white font-medium">{{ friend.username }}</p>
                  <p class="text-xs" :class="friend.is_online ? 'text-emerald-400' : 'text-slate-500'">
                    {{ friend.is_online ? 'Онлайн' : 'Оффлайн' }}
                  </p>
                </div>
              </div>
              <button 
                @click="inviteFriend(friend.id, gameStore.sessionId)"
                v-if="gameStore.sessionId"
                class="p-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors"
                title="Пригласить в игру"
              >
                <Share2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- Сохраненные игры -->
        <div class="bg-slate-900/80 backdrop-blur rounded-2xl border border-white/10 p-6">
          <h2 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Save class="w-5 h-5 text-emerald-400" />
            Мои игры
          </h2>
          
          <div v-if="isLoading" class="text-center text-slate-500 py-8">
            Загрузка...
          </div>
          
          <div v-else-if="!savedGames || savedGames.length === 0" class="text-center text-slate-500 py-8">
            У вас нет активных игр
          </div>
          
          <div v-else class="space-y-2">
            <div v-for="game in savedGames" :key="game.id" class="p-3 bg-slate-800/30 rounded-xl hover:bg-slate-800/50 transition-colors">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-white font-medium">{{ game.name }}</p>
                  <p class="text-xs text-slate-400">{{ game.players?.length || 0 }} игроков • {{ game.max_players }} макс.</p>
                </div>
                <router-link
                  :to="`/game/${game.id}`"
                  class="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 text-white text-sm rounded-lg transition-colors flex items-center gap-2"
                >
                  <Gamepad2 class="w-4 h-4" />
                  Играть
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>