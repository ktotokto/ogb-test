import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useGameStore = defineStore('game', () => {
  // State
  const sessionId = ref(null)
  const session = ref(null)
  const players = ref([])
  const currentPlayer = ref(null)
  const objects = ref([])
  const drawings = ref([])
  const chatMessages = ref([])
  const settings = ref({
    gridEnabled: true,
    gridSize: 50,
    snapToGrid: false
  })
  const isLoading = ref(false)
  const error = ref(null)

  // Computed
  const isAdmin = computed(() => {
    return currentPlayer.value?.role === 'creator' || currentPlayer.value?.role === 'admin'
  })

  async function joinSession(sessionIdValue) {
    if (!sessionIdValue) {
      throw new Error('Session ID is required')
    }

    isLoading.value = true
    error.value = null

    try {
      console.log('🚪 Joining session via WebSocket:', sessionIdValue)

      const { useGameWebSocket } = await import('@/composables/useGameWebSocket')
      const { joinSession: wsJoinSession } = useGameWebSocket()

      wsJoinSession(sessionIdValue)  // ← WebSocket emit

      // Ждём пока сервер отправит session:joined который обновит store
      await new Promise(resolve => setTimeout(resolve, 1000))

      console.log('✅ Session joined:', sessionId.value)

      return session.value
    } catch (err) {
      console.error('❌ Failed to join session:', err)
      error.value = 'Failed to join session'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createSession(options = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/game/session/create', {
        name: options.name || 'New Game',
        isPrivate: options.isPrivate || false,
        maxPlayers: options.maxPlayers || 8
      })

      sessionId.value = response.data.session.id
      session.value = response.data.session
      players.value = response.data.session.players || []

      const userStore = (await import('@/stores/user')).useUserStore()
      currentPlayer.value = players.value.find(
        p => p.user_id === userStore.userId
      )

      return response.data.session
    } catch (err) {
      console.error('❌ Failed to create session:', err)
      error.value = err.response?.data?.error || 'Failed to create session'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function setSession(sessionData) {
    sessionId.value = sessionData.id
    session.value = sessionData

    // ✅ Обновляем игроков
    if (sessionData.players) {
      players.value = sessionData.players
    }

    if (sessionData.state) {
      const state = typeof sessionData.state === 'string'
        ? JSON.parse(sessionData.state)
        : sessionData.state
      objects.value = state.objects || []
      drawings.value = state.drawings || []
      if (state.settings) {
        settings.value = { ...settings.value, ...state.settings }
      }
    }
  }

  function setCurrentPlayer(player) {
    currentPlayer.value = player
    console.log('👤 Current player set:', player)
  }

  function addPlayer(player) {
    const existing = players.value.find(p => p.user_id === player.user_id || p.id === player.id)
    if (!existing) {
      players.value.push(player)
      console.log('👥 Player added:', player)
    }
  }

  function removePlayer(playerId) {
    const before = players.value.length
    players.value = players.value.filter(p => p.user_id !== playerId && p.id !== playerId)
    console.log(`👥 Player removed: ${playerId} (${before} -> ${players.value.length})`)

    if (currentPlayer.value?.user_id === playerId) {
      currentPlayer.value = null
    }
  }

  function updatePlayer(playerId, updates) {
    const player = players.value.find(p => p.user_id === playerId || p.id === playerId)
    if (player) {
      Object.assign(player, updates)
    }
  }

  function clearSession() {
    sessionId.value = null
    session.value = null
    players.value = []
    currentPlayer.value = null
    objects.value = []
    drawings.value = []
    chatMessages.value = []
  }

  function addObject(obj) {
    const existing = objects.value.find(o => o.id === obj.id)
    if (!existing) {
      objects.value.push(obj)
      console.log('🎮 Object added:', obj.id)

      debouncedSave()
    }
  }

  function updateObject(objectId, updates) {
    const obj = objects.value.find(o => o.id === objectId)
    if (obj) {
      Object.assign(obj, updates)
      console.log('Object updated:', objectId, updates)

      debouncedSave()
    }
  }

  function removeObject(objectId) {
    const before = objects.value.length
    objects.value = objects.value.filter(o => o.id !== objectId)
    console.log(`🎮 Object removed: ${objectId} (${before} -> ${objects.value.length})`)

    debouncedSave()
  }


  let saveTimeout = null
  async function debouncedSave() {
    if (saveTimeout) clearTimeout(saveTimeout)

    saveTimeout = setTimeout(async () => {
      if (!sessionId.value) return

      try {
        const state = {
          objects: objects.value,
          drawings: drawings.value,
          settings: settings.value
        }

        await axios.post(`/api/game/session/${sessionId.value}/save`, { state })
        console.log('✅ Auto-saved game state')
      } catch (err) {
        console.error('❌ Auto-save failed:', err)
      }
    }, 2000)
  }

  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      if (sessionId.value && objects.value.length > 0) {
        const state = {
          objects: objects.value,
          drawings: drawings.value,
          settings: settings.value
        }

        navigator.sendBeacon(
          `/api/game/session/${sessionId.value}/save`,
          JSON.stringify({ state })
        )
      }
    })
  }


  function addDrawing(drawing) {
    drawings.value.push(drawing)
  }

  function addChatMessage(message) {
    chatMessages.value.push(message)
    if (chatMessages.value.length > 100) {
      chatMessages.value.shift()
    }
  }

  function updateSetting(key, value) {
    settings.value[key] = value
  }

  return {
    // State
    sessionId,
    session,
    players,
    currentPlayer,
    objects,
    drawings,
    chatMessages,
    settings,
    isLoading,
    error,
    // Computed
    isAdmin,
    // Actions
    debouncedSave,
    joinSession,
    createSession,
    setSession,
    setCurrentPlayer,
    addPlayer,
    removePlayer,
    updatePlayer,
    clearSession,
    addObject,
    updateObject,
    removeObject,
    addDrawing,
    addChatMessage,
    updateSetting
  }
})