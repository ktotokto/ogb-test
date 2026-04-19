import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSocket } from '@/composables/useSocket'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const useGameStore = defineStore('game', () => {
  const sessionId = ref(null)
  const sessionName = ref('')
  const players = ref([])
  const objects = ref([])
  const drawings = ref([])
  const cardDeck = ref([])
  const currentPlayerId = ref(null)
  const chatMessages = ref([])
  const settings = ref({
    gridEnabled: true,
    gridSize: 20,
    snapToGrid: true
  })
  const timer = ref(0)

  const isAdmin = computed(() => {
    const player = players.value.find(p => p.id === currentPlayerId.value)
    return player?.role === 'admin' || player?.role === 'creator'
  })

  const currentPlayer = computed(() => {
    return players.value.find(p => p.id === currentPlayerId.value)
  })

  // --- API calls ---

  async function createSession(name) {
    const token = localStorage.getItem('accessToken')
    const response = await axios.post(`${API_URL}/api/game/sessions`, { name }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    const session = response.data.session
    sessionId.value = session.id
    sessionName.value = session.name
    objects.value = session.state.objects || []
    drawings.value = session.state.drawings || []
    cardDeck.value = session.state.cardDeck || []
    players.value = session.players
    return session
  }

  async function joinSession(sessionIdValue) {
    const token = localStorage.getItem('accessToken')
    const response = await axios.post(`${API_URL}/api/game/sessions/${sessionIdValue}/join`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    const session = response.data.session
    sessionId.value = session.id
    sessionName.value = session.name
    objects.value = session.state.objects || []
    drawings.value = session.state.drawings || []
    cardDeck.value = session.state.cardDeck || []
    players.value = session.players
    return session
  }

  async function fetchSession(sessionIdValue) {
    const token = localStorage.getItem('accessToken')
    const response = await axios.get(`${API_URL}/api/game/sessions/${sessionIdValue}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    const session = response.data.session
    sessionId.value = session.id
    sessionName.value = session.name
    objects.value = session.state.objects || []
    drawings.value = session.state.drawings || []
    cardDeck.value = session.state.cardDeck || []
    players.value = session.players
    return session
  }

  async function fetchSessions() {
    const token = localStorage.getItem('accessToken')
    const response = await axios.get(`${API_URL}/api/game/sessions`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    return response.data
  }

  // --- Socket.IO integration ---

  function setupSocketListeners() {
    const socket = useSocket()

    socket.on('session-state', (data) => {
      sessionId.value = data.sessionId
      objects.value = data.state.objects || []
      drawings.value = data.state.drawings || []
      cardDeck.value = data.state.cardDeck || []
      players.value = data.players
    })

    socket.on('player-online', (data) => {
      if (!players.value.find(p => p.id === data.user.id)) {
        players.value.push(data.user)
      }
    })

    socket.on('player-offline', (data) => {
      players.value = players.value.filter(p => p.id !== data.userId)
    })

    socket.on('object-move', (data) => {
      const obj = objects.value.find(o => o.id === data.objectId)
      if (obj) {
        obj.position = data.position
      }
    })

    socket.on('object-select', (data) => {
      // Можно подсветить выделение другого игрока
    })

    socket.on('object-flip', (data) => {
      const obj = objects.value.find(o => o.id === data.objectId)
      if (obj) obj.faceUp = data.faceUp
    })

    socket.on('object-rotate', (data) => {
      const obj = objects.value.find(o => o.id === data.objectId)
      if (obj) obj.rotation = data.rotation
    })

    socket.on('object-delete', (data) => {
      objects.value = objects.value.filter(o => o.id !== data.objectId)
    })

    socket.on('object-add', (data) => {
      if (!objects.value.find(o => o.id === data.object.id)) {
        objects.value.push(data.object)
      }
    })

    socket.on('stack-add', (data) => {
      const target = objects.value.find(o => o.id === data.targetId)
      const source = objects.value.find(o => o.id === data.sourceId)
      if (target && source) {
        const stackId = target.stackId || target.id
        target.stackId = stackId
        source.stackId = stackId
        const stackCards = objects.value.filter(o => o.stackId === stackId)
        stackCards.forEach((card, i) => { card.stackIndex = i })
      }
    })

    socket.on('stack-remove', (data) => {
      const obj = objects.value.find(o => o.id === data.objectId)
      if (obj) {
        const stackCards = objects.value.filter(o => o.stackId === obj.stackId && o.id !== obj.id)
        obj.stackId = null
        obj.stackIndex = 0
        if (stackCards.length > 0) {
          stackCards.forEach((card, i) => { card.stackIndex = i })
        }
      }
    })

    socket.on('draw-update', (data) => {
      drawings.value = data.drawings
    })

    socket.on('draw-clear', () => {
      drawings.value = []
    })

    socket.on('chat-message', (data) => {
      chatMessages.value.push(data)
    })

    socket.on('state-saved', (data) => {
      console.log('[Game] State saved:', data.sessionId)
    })
  }

  function joinSocketSession(sessionIdValue) {
    const socket = useSocket()
    socket.joinSession(sessionIdValue)
  }

  function leaveSocketSession(sessionIdValue) {
    const socket = useSocket()
    socket.leaveSession(sessionIdValue)
  }

  // --- Actions ---

  function addObject(obj) {
    objects.value.push(obj)
    const socket = useSocket()
    if (sessionId.value) {
      socket.emitObjectAdd(sessionId.value, obj)
    }
  }

  function updateObject(obj) {
    const index = objects.value.findIndex(o => o.id === obj.id)
    if (index !== -1) {
      objects.value[index] = { ...objects.value[index], ...obj }
    }
    const socket = useSocket()
    if (sessionId.value && obj.position) {
      socket.emitObjectMove(sessionId.value, obj.id, obj.position)
    }
  }

  function removeObject(objectId) {
    objects.value = objects.value.filter(o => o.id !== objectId)
    const socket = useSocket()
    if (sessionId.value) {
      socket.emitObjectDelete(sessionId.value, objectId)
    }
  }

  function flipObject(objectId, faceUp) {
    const obj = objects.value.find(o => o.id === objectId)
    if (obj) obj.faceUp = faceUp
    const socket = useSocket()
    if (sessionId.value) {
      socket.emitObjectFlip(sessionId.value, objectId, faceUp)
    }
  }

  function rotateObject(objectId, rotation) {
    const obj = objects.value.find(o => o.id === objectId)
    if (obj) obj.rotation = rotation
    const socket = useSocket()
    if (sessionId.value) {
      socket.emitObjectRotate(sessionId.value, objectId, rotation)
    }
  }

  function updateDrawings(newDrawings) {
    drawings.value = newDrawings
    const socket = useSocket()
    if (sessionId.value) {
      socket.emitDrawUpdate(sessionId.value, newDrawings)
    }
  }

  function clearDrawings() {
    drawings.value = []
    const socket = useSocket()
    if (sessionId.value) {
      socket.emitDrawClear(sessionId.value)
    }
  }

  function sendChatMessage(message) {
    const socket = useSocket()
    if (sessionId.value) {
      socket.emitChatMessage(sessionId.value, message)
    }
  }

  async function saveState() {
    const socket = useSocket()
    const state = {
      objects: objects.value,
      drawings: drawings.value,
      cardDeck: cardDeck.value
    }
    if (sessionId.value) {
      socket.emitSaveState(sessionId.value, state)
      // Also save to DB
      const token = localStorage.getItem('accessToken')
      await axios.put(`${API_URL}/api/game/sessions/${sessionId.value}/state`, { state }, {
        headers: { Authorization: `Bearer ${token}` }
      })
    }
  }

  function addPlayer(player) {
    const existing = players.value.find(p => p.id === player.id)
    if (!existing) players.value.push(player)
  }

  function reset() {
    sessionId.value = null
    sessionName.value = ''
    players.value = []
    objects.value = []
    drawings.value = []
    cardDeck.value = []
    chatMessages.value = []
  }

  return {
    sessionId,
    sessionName,
    players,
    objects,
    drawings,
    cardDeck,
    currentPlayerId,
    chatMessages,
    settings,
    timer,
    isAdmin,
    currentPlayer,
    createSession,
    joinSession,
    fetchSession,
    fetchSessions,
    setupSocketListeners,
    joinSocketSession,
    leaveSocketSession,
    addObject,
    updateObject,
    removeObject,
    flipObject,
    rotateObject,
    updateDrawings,
    clearDrawings,
    sendChatMessage,
    saveState,
    addPlayer,
    reset
  }
})
