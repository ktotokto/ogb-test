<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useGameWebSocket } from '@/composables/useGameWebSocket'
import { UserPlus, UserCheck, UserX, Search, Send } from 'lucide-vue-next'

const userStore = useUserStore()
const { sendFriendRequest, acceptFriendRequest, declineFriendRequest, inviteToSession } = useGameWebSocket()

const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)

const friends = computed(() => userStore.friends)
const requests = computed(() => userStore.friendRequests)

const searchUsers = async () => {
  if (searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  
  isSearching.value = true
  try {
    const response = await fetch(`/api/users/search?query=${encodeURIComponent(searchQuery.value)}`, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    searchResults.value = await response.json()
  } catch (err) {
    console.error('Search failed:', err)
  } finally {
    isSearching.value = false
  }
}

const handleSendRequest = async (userId) => {
  await sendFriendRequest(userId)
  searchResults.value = searchResults.value.filter(u => u.id !== userId)
}

const handleAcceptRequest = (friendshipId) => {
  acceptFriendRequest(friendshipId)
  userStore.removeFriendRequest(friendshipId)
}

const handleDeclineRequest = (friendshipId) => {
  declineFriendRequest(friendshipId)
  userStore.removeFriendRequest(friendshipId)
}

const handleInvite = (sessionId, friendId) => {
  inviteToSession(sessionId, friendId)
}

onMounted(() => {
  userStore.fetchProfile()
})
</script>

<template>
  <div class="w-80 h-full bg-slate-900/90 backdrop-blur border-r border-white/10 flex flex-col">
    <!-- Header -->
    <div class="p-4 border-b border-white/10">
      <h2 class="font-bold text-lg">Друзья</h2>
      <p class="text-sm text-slate-400">{{ friends.length }} друзей • {{ requests.length }} запросов</p>
    </div>

    <!-- Search -->
    <div class="p-4 border-b border-white/10">
      <div class="relative">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          v-model="searchQuery"
          @input="searchUsers"
          type="text"
          placeholder="Поиск пользователей..."
          class="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-800/50 border border-white/10 text-sm focus:outline-none focus:border-violet-500"
        />
      </div>
      
      <!-- Search Results -->
      <div v-if="searchQuery.length >= 2" class="mt-2 max-h-48 overflow-y-auto">
        <div v-for="user in searchResults" :key="user.id" class="flex items-center justify-between p-2 hover:bg-slate-800/50 rounded-lg">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center text-sm">
              {{ user.username[0].toUpperCase() }}
            </div>
            <div>
              <p class="text-sm font-medium">{{ user.username }}</p>
              <p class="text-xs text-slate-400">{{ user.is_online ? '🟢 Онлайн' : '⚪ Оффлайн' }}</p>
            </div>
          </div>
          <button
            @click="handleSendRequest(user.id)"
            class="p-2 rounded-lg hover:bg-violet-600/20 text-violet-400 transition-colors"
            title="Добавить в друзья"
          >
            <UserPlus class="w-4 h-4" />
          </button>
        </div>
        <p v-if="searchResults.length === 0 && !isSearching" class="text-xs text-slate-500 text-center py-2">
          Ничего не найдено
        </p>
      </div>
    </div>

    <!-- Friend Requests -->
    <div v-if="requests.length > 0" class="p-4 border-b border-white/10">
      <h3 class="text-sm font-semibold text-slate-300 mb-2">Запросы в друзья</h3>
      <div class="space-y-2">
        <div v-for="req in requests" :key="req.friendship.id" class="flex items-center justify-between p-2 bg-slate-800/30 rounded-lg">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center text-sm">
              {{ req.requester.username[0].toUpperCase() }}
            </div>
            <span class="text-sm">{{ req.requester.username }}</span>
          </div>
          <div class="flex gap-1">
            <button @click="handleAcceptRequest(req.friendship.id)" class="p-1.5 rounded hover:bg-emerald-600/20 text-emerald-400" title="Принять">
              <UserCheck class="w-4 h-4" />
            </button>
            <button @click="handleDeclineRequest(req.friendship.id)" class="p-1.5 rounded hover:bg-red-600/20 text-red-400" title="Отклонить">
              <UserX class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Friends List -->
    <div class="flex-1 overflow-y-auto p-4">
      <h3 class="text-sm font-semibold text-slate-300 mb-2">Список друзей</h3>
      <div v-if="friends.length === 0" class="text-center text-slate-500 text-sm py-8">
        У вас пока нет друзей
      </div>
      <div v-else class="space-y-2">
        <div v-for="friend in friends" :key="friend.id" class="flex items-center justify-between p-2 hover:bg-slate-800/50 rounded-lg group">
          <div class="flex items-center gap-2">
            <div class="relative">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center text-sm">
                {{ friend.username[0].toUpperCase() }}
              </div>
              <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-slate-900" :class="friend.is_online ? 'bg-emerald-400' : 'bg-slate-500'" />
            </div>
            <div>
              <p class="text-sm font-medium">{{ friend.username }}</p>
              <p class="text-xs text-slate-400">{{ friend.is_online ? 'Онлайн' : 'Оффлайн' }}</p>
            </div>
          </div>
          <button
            v-if="friend.is_online && gameStore.sessionId"
            @click="handleInvite(gameStore.sessionId, friend.id)"
            class="p-1.5 rounded-lg hover:bg-violet-600/20 text-violet-400 opacity-0 group-hover:opacity-100 transition-all"
            title="Пригласить в игру"
          >
            <Send class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>