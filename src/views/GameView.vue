<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import GamePage from '@/components/gamePage/gamePage.vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useGameWebSocket } from '@/composables/useGameWebSocket'


const route = useRoute()
const sessionId = route.params.sessionId
const gameStore = useGameStore()
const userStore = useUserStore()
const isLoading = ref(true)

const { connect, isConnected, joinSession } = useGameWebSocket()

onMounted(async () => {
  if (userStore.isAuthenticated && userStore.token && !isConnected.value) {
    connect(userStore.token)
    
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
  
  
  const targetSessionId = sessionId || localStorage.getItem('lastSessionId')
  
  if (targetSessionId && isConnected.value) {
    try {
      
      joinSession(targetSessionId)
      
      localStorage.setItem('lastSessionId', targetSessionId)
      
      await new Promise(resolve => setTimeout(resolve, 1000))
      
    } catch (e) {
      console.error('Failed to join session:', e)
    }
  }
  
  isLoading.value = false
})

</script>

<template>
  <div class="h-screen bg-slate-950 flex flex-col">
    <div v-if="isLoading" class="h-full flex items-center justify-center">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-white text-lg">Загрузка игры...</p>
      </div>
    </div>
    
    <template v-else>
      <GamePage :session-id="gameStore.sessionId || sessionId" />
    </template>
  </div>
</template>