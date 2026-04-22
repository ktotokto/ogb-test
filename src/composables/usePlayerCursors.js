import { ref, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'

export function usePlayerCursors(socket, gameStore) {
  const otherCursors = ref({})
  const userStore = useUserStore()
  
  const getUserColor = (userId) => {
    const colors = ['#f43f5e', '#06b6d4', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899']
    let hash = 0
    for (let i = 0; i < userId.length; i++) {
      hash = userId.charCodeAt(i) + ((hash << 5) - hash)
    }
    return colors[Math.abs(hash) % colors.length]
  }
  
  const sendCursorMove = (x, y) => {
    if (!socket.value || !gameStore.sessionId) return
    socket.value.emit('cursor:move', {
      sessionId: gameStore.sessionId,
      cursor: { x, y, timestamp: Date.now() }
    })
  }
  
  const sendCursorLeave = () => {
    if (!socket.value || !gameStore.sessionId) return
    socket.value.emit('cursor:leave', { sessionId: gameStore.sessionId })
  }
  
  const setupListeners = () => {
    if (!socket.value) return
    
    socket.value.on('cursor:move', (data) => {
      console.log('📥 Cursor move received:', data)
      
      if (data.sessionId !== gameStore.sessionId) return
      if (data.userId === userStore.userId) return
      
      otherCursors.value[data.userId] = {
        x: data.cursor.x,
        y: data.cursor.y,
        username: data.username || 'Player',  // ← username из бэкенда!
        color: getUserColor(data.userId),
        lastSeen: Date.now()
      }
    })
    
    socket.value.on('cursor:leave', (data) => {
      console.log('📥 Cursor leave received:', data)
      if (data.sessionId !== gameStore.sessionId) return
      delete otherCursors.value[data.userId]
    })
    
    const cleanupInterval = setInterval(() => {
      const now = Date.now()
      Object.entries(otherCursors.value).forEach(([userId, cursor]) => {
        if (now - cursor.lastSeen > 5000) {
          delete otherCursors.value[userId]
        }
      })
    }, 2000)
    
    return () => clearInterval(cleanupInterval)
  }
  
  const cleanup = setupListeners()
  
  onUnmounted(() => {
    sendCursorLeave()
    if (cleanup) cleanup()
  })
  
  return {
    otherCursors,
    sendCursorMove,
    sendCursorLeave,
    getUserColor
  }
}