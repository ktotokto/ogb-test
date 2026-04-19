import { ref } from 'vue'
import { io } from 'socket.io-client'

const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

let socket = null
const isConnected = ref(false)
const listeners = new Map()

export function useSocket() {
  const connect = (token) => {
    if (socket?.connected) return

    socket = io(SOCKET_URL, {
      query: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    })

    socket.on('connect', () => {
      isConnected.value = true
      listeners.forEach((cb, event) => {
        socket.on(event, cb)
      })
    })

    socket.on('disconnect', () => {
      isConnected.value = false
    })

    socket.on('error', (data) => {
      console.error('[Socket] Error:', data)
    })
  }

  const disconnect = () => {
    if (socket) {
      listeners.forEach((cb, event) => {
        socket.off(event, cb)
      })
      listeners.clear()
      socket.disconnect()
      socket = null
      isConnected.value = false
    }
  }

  const emit = (event, data) => {
    if (socket?.connected) {
      socket.emit(event, data)
    }
  }

  const on = (event, callback) => {
    listeners.set(event, callback)
    if (socket?.connected) {
      socket.on(event, callback)
    }
  }

  const off = (event) => {
    listeners.delete(event)
    if (socket?.connected) {
      socket.off(event)
    }
  }

  const joinSession = (sessionId) => {
    emit('join-session', { sessionId })
  }

  const leaveSession = (sessionId) => {
    emit('leave-session', { sessionId })
  }

  const emitObjectMove = (sessionId, objectId, position) => {
    emit('object-move', { sessionId, objectId, position })
  }

  const emitObjectSelect = (sessionId, objectId) => {
    emit('object-select', { sessionId, objectId })
  }

  const emitObjectFlip = (sessionId, objectId, faceUp) => {
    emit('object-flip', { sessionId, objectId, faceUp })
  }

  const emitObjectRotate = (sessionId, objectId, rotation) => {
    emit('object-rotate', { sessionId, objectId, rotation })
  }

  const emitObjectDelete = (sessionId, objectId) => {
    emit('object-delete', { sessionId, objectId })
  }

  const emitObjectAdd = (sessionId, object) => {
    emit('object-add', { sessionId, object })
  }

  const emitStackAdd = (sessionId, targetId, sourceId) => {
    emit('stack-add', { sessionId, targetId, sourceId })
  }

  const emitStackRemove = (sessionId, objectId) => {
    emit('stack-remove', { sessionId, objectId })
  }

  const emitDrawUpdate = (sessionId, drawings) => {
    emit('draw-update', { sessionId, drawings })
  }

  const emitDrawClear = (sessionId) => {
    emit('draw-clear', { sessionId })
  }

  const emitSaveState = (sessionId, state) => {
    emit('save-state', { sessionId, state })
  }

  const emitChatMessage = (sessionId, message) => {
    emit('chat-message', { sessionId, message })
  }

  return {
    isConnected,
    connect,
    disconnect,
    emit,
    on,
    off,
    joinSession,
    leaveSession,
    emitObjectMove,
    emitObjectSelect,
    emitObjectFlip,
    emitObjectRotate,
    emitObjectDelete,
    emitObjectAdd,
    emitStackAdd,
    emitStackRemove,
    emitDrawUpdate,
    emitDrawClear,
    emitSaveState,
    emitChatMessage
  }
}
