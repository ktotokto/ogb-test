import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  const router = useRouter()

  const currentUser = ref(null)
  const userId = computed(() => currentUser.value?.id)
  const token = ref(localStorage.getItem('token') || null)
  const isLoading = ref(false)
  const error = ref(null)

  const friends = ref([])
  const friendRequests = ref([])

  const isAuthenticated = computed(() => !!token.value && !!currentUser.value)
  const onlineFriends = computed(() => friends.value.filter(f => f.is_online))

  async function initAuth() {
    const savedToken = localStorage.getItem('token')
    if (savedToken && !currentUser.value) {
      token.value = savedToken
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`

      try {
        const response = await axios.get('/api/auth/me')
        currentUser.value = response.data.user || response.data
      } catch (err) {
        logout()
      }
    }
  }

  async function login(username, password) {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/auth/login', { username, password })

      token.value = response.data.accessToken
      localStorage.setItem('token', token.value)
      currentUser.value = response.data.user

      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`

      await router.push('/')

      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Login failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function register(username, email, password) {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/auth/register', { username, email, password })

      token.value = response.data.accessToken
      localStorage.setItem('token', token.value)
      currentUser.value = response.data.user

      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`

      await router.push('/')

      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Registration failed'
      console.error('Register error:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    token.value = null
    currentUser.value = null
    friends.value = []
    friendRequests.value = []
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    router.push('/login')
  }

  async function fetchFriends() {
    try {
      const response = await axios.get('/api/friends')
      friends.value = (response.data || []).map(f => f.user)
    } catch (err) {
      console.error('Failed to fetch friends:', err)
      friends.value = []  // Защита
    }
  }

  async function fetchFriendRequests() {
    try {
      const response = await axios.get('/api/friends/requests')
      friendRequests.value = response.data || []
    } catch (err) {
      console.error('Failed to fetch requests:', err)
      friendRequests.value = []  // Защита
    }
  }

  function removeFriendRequest(friendshipId) {
    friendRequests.value = friendRequests.value.filter(
      r => r.friendship?.id !== friendshipId
    )
  }


  function setFriends(list) {
    friends.value = Array.isArray(list) ? list : []
  }

  function setFriendRequests(list) {
    friendRequests.value = Array.isArray(list) ? list : []
  }

  function addFriend(friend) {
    if (!friends.value.find(f => f.id === friend.id)) {
      friends.value.push(friend)
    }
  }

  function removeFriend(friendId) {
    friends.value = friends.value.filter(f => f.id !== friendId)
  }

  function updateFriendStatus(friendId, isOnline) {
    const friend = friends.value.find(f => f.id === friendId)
    if (friend) {
      friend.is_online = isOnline
    }
  }

  initAuth()

  return {
    currentUser,
    token,
    isLoading,
    error,
    friends,
    friendRequests,
    isAuthenticated,
    onlineFriends,
    userId,
    login,
    register,
    logout,
    initAuth,
    fetchFriends,
    fetchFriendRequests,
    removeFriendRequest,
    addFriend,
    removeFriend,
    updateFriendStatus,
    setFriends,
    setFriendRequests
  }
})