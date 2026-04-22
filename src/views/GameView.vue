<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GamePage from '@/components/gamePage/gamePage.vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useGameWebSocket } from '@/composables/useGameWebSocket'
import { Save, Share2 } from 'lucide-vue-next'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const sessionId = route.params.sessionId
const gameStore = useGameStore()
const userStore = useUserStore()
const showInviteModal = ref(false)
const isLoading = ref(true)

// ✅ Правильная деструктуризация из composable
const { socket, connect, isConnected, joinSession } = useGameWebSocket()

console.log('🎮 GameView mounted, sessionId:', sessionId)

const saveGame = async () => {
  try {
    const state = {
      objects: gameStore.objects,
      drawings: gameStore.drawings,
      settings: gameStore.settings
    }
    
    await axios.post(`/api/game/session/${gameStore.sessionId}/save`, { state })
    console.log('✅ Game saved')
  } catch (err) {
    console.error('Failed to save:', err)
  }
}

const inviteFriend = async (friendId) => {
  try {
    await axios.post('/api/game/session/invite', {
      sessionId: gameStore.sessionId,
      receiverId: friendId
    })
    alert('Приглашение отправлено!')
    showInviteModal.value = false
  } catch (err) {
    console.error('Failed to invite:', err)
    alert('Ошибка при отправке приглашения')
  }
}

onMounted(async () => {
  console.log('🎮 GameView onMounted')
  console.log('🔐 isAuthenticated:', userStore.isAuthenticated)
  console.log('🎫 Token exists:', !!userStore.token)
  
  // 1. Подключение к WebSocket
  if (userStore.isAuthenticated && userStore.token && !isConnected.value) {
    console.log('🔌 Connecting to WebSocket...')
    connect(userStore.token)
    
    // Ждём подключения (макс 5 сек)
    await new Promise(resolve => {
      const checkConnection = setInterval(() => {
        if (isConnected.value) {
          clearInterval(checkConnection)
          resolve()
        }
      }, 100)
      setTimeout(() => {
        clearInterval(checkConnection)
        resolve()
      }, 5000)
    })
  }
  
  console.log('📡 Socket connected:', isConnected.value)
  
  // 2. Определяем sessionId
  const targetSessionId = sessionId || localStorage.getItem('lastSessionId')
  
  if (targetSessionId && isConnected.value) {
    try {
      console.log('🚪 Joining session:', targetSessionId)
      
      joinSession(targetSessionId)
      
      // Сохраняем в localStorage
      localStorage.setItem('lastSessionId', targetSessionId)
      
      // Ждём загрузки сессии
      await new Promise(resolve => setTimeout(resolve, 1000))
      
    } catch (e) {
      console.error('❌ Failed to join session:', e)
    }
  }
  
  isLoading.value = false
  
  // 3. Логирование
  setTimeout(() => {
    console.log('📊 GameStore state after mount:')
    console.log('  - sessionId:', gameStore.sessionId)
    console.log('  - players:', gameStore.players)
    console.log('  - currentPlayer:', gameStore.currentPlayer)
    console.log('  - objects:', gameStore.objects.length)
  }, 1000)
})

onUnmounted(() => {
  console.log('👋 GameView onUnmounted')
})
</script>

<template>
  <div class="h-screen bg-slate-950 flex flex-col">
    <!-- Loading -->
    <div v-if="isLoading" class="h-full flex items-center justify-center">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-white text-lg">Загрузка игры...</p>
      </div>
    </div>
    
    <!-- Game Content -->
    <template v-else>
      <GamePage :session-id="gameStore.sessionId || sessionId" />
      
      <div class="absolute top-25 right-6 flex gap-2 z-50">
        <button @click="saveGame"
          class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-all shadow-lg flex items-center gap-2"
          title="Сохранить игру">
          <Save class="w-4 h-4" />
          <span class="hidden md:inline">Сохранить</span>
        </button>

        <button @click="showInviteModal = true"
          class="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg transition-all shadow-lg flex items-center gap-2"
          title="Пригласить друзей">
          <Share2 class="w-4 h-4" />
          <span class="hidden md:inline">Пригласить</span>
        </button>
      </div>

      <!-- Modal для приглашений -->
      <div v-if="showInviteModal"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center">
        <div class="bg-slate-900 border border-white/10 rounded-2xl p-6 max-w-md w-full mx-4">
          <h3 class="text-xl font-bold text-white mb-4">Пригласить друзей</h3>

          <div class="space-y-2 max-h-64 overflow-y-auto">
            <div v-for="friend in userStore.friends" :key="friend.id"
              class="flex items-center justify-between p-3 bg-slate-800/30 rounded-xl">
              <div class="flex items-center gap-3">
                <div
                  class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center">
                  <span class="text-xs text-white font-bold">{{ friend.username?.[0]?.toUpperCase() || '?' }}</span>
                </div>
                <span class="text-white text-sm">{{ friend.username }}</span>
              </div>
              <button @click="inviteFriend(friend.id)" class="p-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg">
                <Share2 class="w-4 h-4" />
              </button>
            </div>
          </div>

          <button @click="showInviteModal = false"
            class="mt-4 w-full py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors">
            Закрыть
          </button>
        </div>
      </div>
    </template>
  </div>
</template>