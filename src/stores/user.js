import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSocket } from '@/composables/useSocket'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref(null)
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const isAuthenticated = computed(() => !!accessToken.value && !!currentUser.value)

  const userId = computed(() => currentUser.value?.id)
  const userName = computed(() => currentUser.value?.username)

  async function login(username, password) {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Login failed')
    }

    const data = await response.json()
    accessToken.value = data.accessToken
    currentUser.value = data.user
    localStorage.setItem('accessToken', data.accessToken)

    // Подключить WebSocket
    const { connect } = useSocket()
    connect(data.accessToken)

    return data
  }

  async function register(username, email, password) {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Registration failed')
    }

    const data = await response.json()
    accessToken.value = data.accessToken
    currentUser.value = data.user
    localStorage.setItem('accessToken', data.accessToken)

    // Подключить WebSocket
    const { connect } = useSocket()
    connect(data.accessToken)

    return data
  }

  async function fetchCurrentUser() {
    if (!accessToken.value) return

    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${accessToken.value}` }
      })

      if (response.ok) {
        const data = await response.json()
        currentUser.value = data.user

        // Подключить WebSocket
        const { connect } = useSocket()
        connect(accessToken.value)
      } else {
        logout()
      }
    } catch (e) {
      console.error('Failed to fetch user:', e)
    }
  }

  function logout() {
    const { disconnect } = useSocket()
    disconnect()
    accessToken.value = null
    currentUser.value = null
    localStorage.removeItem('accessToken')
  }

  function setUser(user) {
    currentUser.value = user
  }

  function clearUser() {
    logout()
  }

  // Проверка при загрузке
  if (accessToken.value && !currentUser.value) {
    fetchCurrentUser()
  }

  return {
    currentUser,
    accessToken,
    isAuthenticated,
    userId,
    userName,
    login,
    register,
    logout,
    fetchCurrentUser,
    setUser,
    clearUser
  }
})
