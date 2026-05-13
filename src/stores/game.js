import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'
import axios from 'axios'


export const useGameStore = defineStore('game', () => {
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
  const decks = ref([])
  const selectedForHand = ref(new Set())
  const userStore = useUserStore()

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
      const { useGameWebSocket } = await import('@/composables/useGameWebSocket')
      const { joinSession: wsJoinSession } = useGameWebSocket()

      wsJoinSession(sessionIdValue)

      await new Promise(resolve => setTimeout(resolve, 1000))

      return session.value
    } catch (err) {
      console.error('Failed to join session:', err)
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
      console.error('Failed to create session:', err)
      error.value = err.response?.data?.error || 'Failed to create session'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function addToSelectedForHand(objectId) {
    selectedForHand.value.add(objectId)
  }

  function removeFromSelectedForHand(objectId) {
    selectedForHand.value.delete(objectId)
  }

  function clearSelectedForHand() {
    selectedForHand.value.clear()
  }

  function toggleSelectedForHand(objectId) {
    if (selectedForHand.value.has(objectId)) {
      selectedForHand.value.delete(objectId)
    } else {
      selectedForHand.value.add(objectId)
    }
  }

  function moveSelectedToHand() {
    selectedForHand.value.forEach(objectId => {
      const obj = objects.value.find(o => o.id === objectId)
      if (obj) {
        updateObject(objectId, {
          inHand: true,
          owner: userStore.userId,
          stackId: null,
          stackIndex: 0
        })
      }
    })
    selectedForHand.value.clear()
    debouncedSave()
  }

  function shuffleCards(cardIds) {
    const cards = objects.value.filter(obj => cardIds.includes(obj.id))
    const centerX = 50000
    const centerY = 50000

    cards.forEach((card, index) => {
      const randomX = centerX + (Math.random() - 0.5) * 400
      const randomY = centerY + (Math.random() - 0.5) * 400
      const randomRotation = Math.random() * 20 - 10

      updateObject(card.id, {
        position: { x: randomX, y: randomY },
        rotation: randomRotation
      })
    })

    debouncedSave()
  }

  function shuffleDeck(deckId) {
    const deck = decks.value.find(d => d.id === deckId)
    if (!deck || !deck.cards) return

    const shuffledCards = [...deck.cards].sort(() => Math.random() - 0.5)
    updateDeck(deckId, { cards: shuffledCards })
  }

  function createStack(targetId, sourceId) {
    const target = objects.value.find(o => o.id === targetId)
    const source = objects.value.find(o => o.id === sourceId)
    if (!target || !source) return

    const stackId = target.stackId || target.id

    updateObject(targetId, { stackId, stackIndex: 0 })
    updateObject(sourceId, { stackId, stackIndex: 1 })

    debouncedSave()
  }

  function addToStack(stackId, objectId) {
    const stackCards = objects.value.filter(o => o.stackId === stackId)
    const maxIndex = stackCards.length > 0
      ? Math.max(...stackCards.map(c => c.stackIndex || 0))
      : -1

    updateObject(objectId, {
      stackId,
      stackIndex: maxIndex + 1
    })

    debouncedSave()
  }

  function removeFromStack(objectId) {
    const obj = objects.value.find(o => o.id === objectId)
    if (!obj || !obj.stackId) return

    updateObject(objectId, {
      stackId: null,
      stackIndex: 0
    })

    const remainingCards = objects.value
      .filter(o => o.stackId === obj.stackId && o.id !== objectId)
      .sort((a, b) => (a.stackIndex || 0) - (b.stackIndex || 0))

    remainingCards.forEach((card, index) => {
      updateObject(card.id, { stackIndex: index })
    })

    debouncedSave()
  }

  function unstackAll(stackId) {
    const stackCards = objects.value.filter(o => o.stackId === stackId)
    const centerX = stackCards[0]?.position.x || 50000
    const centerY = stackCards[0]?.position.y || 50000

    stackCards.forEach((card, index) => {
      updateObject(card.id, {
        stackId: null,
        stackIndex: 0,
        position: {
          x: centerX + (index % 5) * 140 - 280,
          y: centerY + Math.floor(index / 5) * 200
        }
      })
    })

    debouncedSave()
  }

  function setSession(sessionData) {
    sessionId.value = sessionData.id
    session.value = sessionData

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
  function addDeck(deckData, position = { x: 50000, y: 50000 }) {
    if (objects.value.find(o => o.id === deckData.id && o.type === 'deck')) return


    const deck = {
      id: deckData.id || `deck_${Date.now()}`,
      name: deckData.name || 'Новая колода',
      cards: deckData.cards || [],
      cardCount: (deckData.cards || []).length,
      createdAt: new Date().toISOString(),
      createdBy: userStore.userId,
      position: position
    }

    decks.value.push(deck)

    objects.value.push({
      id: deck.id,
      type: 'deck',
      label: deck.name,
      position: position,
      width: 120,
      height: 180,
      rotation: 0,
      owner: userStore.userId,
      ownerId: userStore.userId,
      cards: deck.cards,
      cardCount: deck.cardCount
    })

    debouncedSave()
    return deck
  }

  function updateDeck(deckId, updates) {
    const index = decks.value.findIndex(d => d.id === deckId)
    if (index === -1) return

    decks.value[index] = { ...decks.value[index], ...updates }

    const boardObj = objects.value.find(o => o.id === deckId && o.type === 'deck')
    if (boardObj) {
      Object.assign(boardObj, updates)
      boardObj.cards = decks.value[index].cards
      boardObj.cardCount = decks.value[index].cardCount
    }

    debouncedSave()
  }

  function removeDeck(deckId) {
    decks.value = decks.value.filter(d => d.id !== deckId)
    removeObject(deckId)
  }

  function addCardToDeck(deckId, cardObj) {
    const deck = decks.value.find(d => d.id === deckId)

    if (!deck || !cardObj) { return false }
    if (!deck.cards) deck.cards = []
    if (deck.cards.some(c => c.id === cardObj.id)) { return false }
    
    deck.cards.push({
      id: cardObj.id,
      label: cardObj.label,
      cardData: cardObj.cardData
    })
    deck.cardCount = deck.cards.length

    const boardDeck = objects.value.find(o => o.id === deckId && o.type === 'deck')
    if (boardDeck) {
      boardDeck.cards = [...deck.cards]
      boardDeck.cardCount = deck.cardCount
    }

    debouncedSave()
    return true
  }

  function drawFromDeck(deckId, count = 1, position) {
    const deck = decks.value.find(d => d.id === deckId)
    if (!deck || !deck.cards?.length) return []

    const drawn = []
    const cx = position.x
    const cy = position.y

    const perRow = 5
    const spacingX = 140
    const spacingY = 200
    const cols = Math.min(count, perRow)
    const startX = cx - (cols * spacingX) / 2 + 60
    const startY = cy - 200

    for (let i = 0; i < count && deck.cards.length > 0; i++) {
      const c = deck.cards.pop()
      const row = Math.floor(i / perRow)
      const col = i % perRow

      const card = {
        id: `card_${Date.now()}_${i}`,
        type: 'card',
        label: c.label,
        position: {
          x: startX + col * spacingX,
          y: startY + row * spacingY
        },
        width: 120,
        height: 180,
        rotation: 0,
        owner: userStore.userId,
        ownerId: userStore.userId,
        inHand: false,
        faceUp: true,
        cardData: c.cardData,
        fromDeck: deckId
      }

      objects.value.push(card)
      drawn.push(card)
    }

    deck.cardCount = deck.cards.length
    const boardObj = objects.value.find(o => o.id === deckId && o.type === 'deck')
    if (boardObj) {
      boardObj.cards = deck.cards
      boardObj.cardCount = deck.cardCount
    }

    debouncedSave()
    return drawn
  }

  function shuffleDeck(deckId) {
    const deck = decks.value.find(d => d.id === deckId)
    if (!deck?.cards) return
    deck.cards.sort(() => Math.random() - 0.5)
    const boardObj = objects.value.find(o => o.id === deckId && o.type === 'deck')
    if (boardObj) boardObj.cards = deck.cards
    debouncedSave()
  }



  function spreadDeck(deckId, position) {
    const deck = decks.value.find(d => d.id === deckId)
    if (!deck?.cards?.length) return []

    const spread = []
    const cx = position?.x || 50000
    const cy = position?.y || 50000
    const perRow = 5
    const toSpread = [...deck.cards]
    deck.cards = []
    deck.cardCount = 0

    toSpread.forEach((c, i) => {
      const row = Math.floor(i / perRow)
      const col = i % perRow
      const card = {
        id: `card_${Date.now()}_${i}`,
        type: 'card', label: c.label,
        position: { x: cx + col * 140 - 280, y: cy + row * 200 - 200 },
        width: 120, height: 180, rotation: 0,
        owner: userStore.userId, ownerId: userStore.userId,
        inHand: false, faceUp: true, cardData: c.cardData, fromDeck: deckId
      }
      objects.value.push(card)
      spread.push(card)
    })

    const boardObj = objects.value.find(o => o.id === deckId && o.type === 'deck')
    if (boardObj) { boardObj.cards = []; boardObj.cardCount = 0 }
    debouncedSave()
    return spread
  }

  function setCurrentPlayer(player) {
    currentPlayer.value = player
  }

  function addPlayer(player) {
    const existing = players.value.find(p => p.user_id === player.user_id || p.id === player.id)
    if (!existing) {
      players.value.push(player)
    }
  }

  function removePlayer(playerId) {
    const before = players.value.length
    players.value = players.value.filter(p => p.user_id !== playerId && p.id !== playerId)

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
    if (objects.value.find(o => o.id === obj.id)) return
    const existing = objects.value.find(o => o.id === obj.id)
    if (!existing) {
      objects.value.push(obj)
      debouncedSave()
    }
  }

  function updateObject(objectId, updates) {
    const obj = objects.value.find(o => o.id === objectId)
    if (obj) {
      Object.assign(obj, updates)
      debouncedSave()
    }
  }

  function removeObject(objectId) {
    objects.value = objects.value.filter(o => o.id !== objectId)
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
      } catch (err) {
        console.error('Auto-save failed:', err)
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
    isAdmin,
    decks,
    selectedForHand,
    addDeck,
    updateDeck,
    removeDeck,
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
    updateSetting,
    drawFromDeck,
    addToSelectedForHand,
    removeFromSelectedForHand,
    clearSelectedForHand,
    toggleSelectedForHand,
    moveSelectedToHand,
    shuffleCards,
    shuffleDeck,
    createStack,
    addToStack,
    removeFromStack,
    unstackAll,
    addCardToDeck,
    spreadDeck
  }
})