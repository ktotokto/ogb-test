import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGameStore = defineStore('game', () => {
    const sessionId = ref(null)
    const players = ref([])
    const objects = ref([])
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

    function addPlayer(player) {
        const existing = players.value.find(p => p.id === player.id)
        if (!existing) players.value.push(player)
    }

    function removeObject(objectId) {
        objects.value = objects.value.filter(o => o.id !== objectId)
    }

    function updateObject(obj) {
        const index = objects.value.findIndex(o => o.id === obj.id)
        if (index !== -1) {
            objects.value[index] = { ...objects.value[index], ...obj }
        }
    }

    return {
        sessionId,
        players,
        objects,
        currentPlayerId,
        chatMessages,
        settings,
        timer,
        isAdmin,
        currentPlayer,
        addPlayer,
        removeObject,
        updateObject
    }
})