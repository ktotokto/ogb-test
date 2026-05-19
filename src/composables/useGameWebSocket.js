import { io } from 'socket.io-client'
import { ref, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useGameStore } from '@/stores/game'
import { tryOnMounted } from '@vueuse/core'

let socketInstance = null
let isConnectedInstance = ref(false)

export function useGameWebSocket() {
  const userStore = useUserStore()
  const gameStore = useGameStore()

  if (!socketInstance) {
    socketInstance = ref(null)
    isConnectedInstance = ref(false)

    const connect = (token) => {
      if (socketInstance.value) socketInstance.value.disconnect()

      socketInstance.value = io(import.meta.env.VITE_WS_URL || 'http://localhost:5000', {
        transports: ['websocket'],
        query: { token },
        auth: { token }
      })

      socketInstance.value.on('connect', () => {
        isConnectedInstance.value = tryOnMounted
        socketInstance.value.emit('friends:get_list')
        socketInstance.value.emit('friends:get_requests')
      })

      socketInstance.value.on('disconnect', () => {
        isConnectedInstance.value = false
      })

      socketInstance.value.on('session:joined', (data) => {
        gameStore.setSession(data.session)
        if (data.players) {
          gameStore.players = data.players
        }
        gameStore.setCurrentPlayer(data.session.players?.find(p => p.user_id === userStore.userId))
      })

      socketInstance.value.on('player:joined', (data) => {
        gameStore.addPlayer(data.player || data.user)
      })

      socketInstance.value.on('player:left', (data) => {
        gameStore.removePlayer(data.userId)
      })

      socketInstance.value.on('object:created', (data) => {
        if (data.sessionId !== gameStore.sessionId) return
        if (data.object.ownerId === userStore.userId || data.userId === userStore.userId) return

        gameStore.addObject(data.object)
      })

      socketInstance.value.on('object:updated', (data) => {
        if (data.sessionId === gameStore.sessionId) {
          gameStore.updateObject(data.objectId, data.updates)
        }
      })

      socketInstance.value.on('object:deleted', (data) => {
        if (data.sessionId === gameStore.sessionId) {
          gameStore.removeObject(data.objectId)
        }
      })

      socketInstance.value.on('object:sync', (data) => {
        if (data.sessionId !== gameStore.sessionId) {
          return
        }

        if (data.userId === userStore.userId) {
          return
        }

        const { objectId, changes } = data.update
        gameStore.updateObject(objectId, changes)
      })

      socketInstance.value.on('drawing:created', (data) => {
        if (data.sessionId === gameStore.sessionId) {
          gameStore.addDrawing(data.drawing)
        }
      })

      socketInstance.value.on('invitation:received', (data) => {
        if (confirm(`${data.sender.username} приглашает вас в игру "${data.session.name}"`)) {
          socketInstance.value.emit('invitation:accept', { invitationId: data.invitation.id })
        }
      })


      socketInstance.value.on('friends:list', (data) => {
        userStore.setFriends(data.friends.map(f => f.user))
      })

      socketInstance.value.on('friends:requests', (data) => {
        userStore.setFriendRequests(data.requests)
      })

      socketInstance.value.on('friend:request_received', (data) => {
        if (confirm(`${data.requester.username} хочет добавить вас в друзья`)) {
          socketInstance.value.emit('friend:accept', { friendshipId: data.friendship.id })
        }
      })

      socketInstance.value.on('friend:accepted', (data) => {
        userStore.addFriend(data.accepter)
      })

      socketInstance.value.on('friend:status_changed', (data) => {
        userStore.updateFriendStatus(data.userId, data.isOnline)
      })
    }

    const disconnect = () => {
      if (socketInstance.value) {
        socketInstance.value.disconnect()
        socketInstance.value = null
        isConnectedInstance.value = false
      }
    }

    watch(() => userStore.token, (newToken) => {
      if (newToken) {
        connect(newToken)
      }
    })

    if (userStore.token) {
      connect(userStore.token)
    }

    socketInstance._connect = connect
    socketInstance._disconnect = disconnect
  }

  const createSession = (options = {}) => {
    if (!socketInstance.value) return
    socketInstance.value.emit('session:create', {
      name: options.name || `${userStore.userName}'s Game`,
      isPrivate: options.isPrivate || false,
      maxPlayers: options.maxPlayers || 8
    })
  }

  const joinSession = (sessionId) => {
    if (!socketInstance.value) return
    socketInstance.value.emit('session:join', { sessionId })
  }

  const leaveSession = () => {
    if (!socketInstance.value || !gameStore.sessionId) return
    socketInstance.value.emit('session:leave', { sessionId: gameStore.sessionId })
    gameStore.clearSession()
  }

  const inviteToSession = (sessionId, receiverId) => {
    if (!socketInstance.value) return
    socketInstance.value.emit('session:invite', { sessionId, receiverId })
  }

  const acceptInvitation = (invitationId) => {
    if (!socketInstance.value) return
    socketInstance.value.emit('invitation:accept', { invitationId })
  }

  const declineInvitation = (invitationId) => {
    if (!socketInstance.value) return
    socketInstance.value.emit('invitation:decline', { invitationId })
  }

  const createObject = (object) => {
    if (!socketInstance.value || !gameStore.sessionId) return
    socketInstance.value.emit('object:create', {
      sessionId: gameStore.sessionId,
      object
    })
  }

  const updateObject = (objectId, updates) => {
    if (!socketInstance.value || !gameStore.sessionId) return
    socketInstance.value.emit('object:update', {
      sessionId: gameStore.sessionId,
      objectId,
      updates
    })
  }

  const deleteObject = (objectId) => {
    if (!socketInstance.value || !gameStore.sessionId) return
    socketInstance.value.emit('object:delete', {
      sessionId: gameStore.sessionId,
      objectId
    })
  }

  const createDrawing = (drawing) => {
    if (!socketInstance.value || !gameStore.sessionId) return
    socketInstance.value.emit('drawing:create', {
      sessionId: gameStore.sessionId,
      drawing
    })
  }

  const sendChatMessage = (message) => {
    if (!socketInstance.value || !gameStore.sessionId) return
    socketInstance.value.emit('chat:send', {
      sessionId: gameStore.sessionId,
      message
    })
  }

  const sendFriendRequest = (receiverId) => {
    if (!socketInstance.value) return
    socketInstance.value.emit('friend:request', { receiverId })
  }

  const acceptFriendRequest = (friendshipId) => {
    if (!socketInstance.value) return
    socketInstance.value.emit('friend:accept', { friendshipId })
  }

  const declineFriendRequest = (friendshipId) => {
    if (!socketInstance.value) return
    socketInstance.value.emit('friend:decline', { friendshipId })
  }

  const removeFriend = (friendId) => {
    if (!socketInstance.value) return
    socketInstance.value.emit('friend:remove', { friendId })
  }

  const refreshFriends = () => {
    if (!socketInstance.value) return
    socketInstance.value.emit('friends:get_list')
    socketInstance.value.emit('friends:get_requests')
  }

  const connect = socketInstance?._connect || (() => { })
  const disconnect = socketInstance?._disconnect || (() => { })


  const emitObjectSync = (objectId, changes, type = 'update') => {
    if (!socket.value || !gameStore.sessionId) return
    socket.value.emit('object:sync', {
      sessionId: gameStore.sessionId,
      userId: userStore.userId,
      update: {
        objectId,
        changes,
        type
      }
    })
  }

  return {
    socket: socketInstance,
    isConnected: isConnectedInstance,
    connect,
    disconnect,
    emitObjectSync,
    createSession,
    joinSession,
    leaveSession,
    inviteToSession,
    acceptInvitation,
    declineInvitation,
    createObject,
    updateObject,
    deleteObject,
    createDrawing,
    sendChatMessage,
    sendFriendRequest,
    acceptFriendRequest,
    declineFriendRequest,
    removeFriend,
    refreshFriends
  }
}