import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref({
    id: 'user_123',
    name: 'Player',
    email: 'player@example.com',
    avatar: '👤'
  })
  const isAuthenticated = ref(true)

  const userId = computed(() => currentUser.value?.id)
  const userName = computed(() => currentUser.value?.name)

  function setUser(user) {
    currentUser.value = user
    isAuthenticated.value = true
  }

  function clearUser() {
    currentUser.value = null
    isAuthenticated.value = false
  }

  return {
    currentUser,
    isAuthenticated,
    userId,
    userName,
    setUser,
    clearUser
  }
})