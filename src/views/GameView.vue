<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GamePage from '@/components/gamePage/gamePage.vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { useSocket } from '@/composables/useSocket'

const route = useRoute()
const router = useRouter()
const sessionId = route.params.sessionId
const gameStore = useGameStore()
const userStore = useUserStore()

onMounted(async () => {
  if (userStore.isAuthenticated) {
    try {
      // Пробуем подключиться к сессии через API
      await gameStore.joinSession(sessionId)

      // Подключаем SocketIO
      gameStore.setupSocketListeners()
      gameStore.joinSocketSession(sessionId)
    } catch (e) {
      console.error('Failed to join session:', e)
    }
  }
})

onUnmounted(() => {
  gameStore.leaveSocketSession(sessionId)
  gameStore.reset()
})
</script>

<template>
  <GamePage :session-id="sessionId" />
</template>
