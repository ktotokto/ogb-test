import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authApi = {
  async login(email, password) {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },

  async register(username, email, password) {
    const response = await api.post('/auth/register', { username, email, password })
    return response.data
  },

  async getProfile() {
    const response = await api.get('/auth/me')
    return response.data
  },

  async updateProfile(data) {
    const response = await api.put('/auth/me', data)
    return response.data
  },

  async changePassword(oldPassword, newPassword) {
    const response = await api.post('/auth/change-password', { oldPassword, newPassword })
    return response.data
  },

  // Friends API
  async getFriends() {
    const response = await api.get('/friends')
    return response.data
  },

  async sendFriendRequest(userId) {
    const response = await api.post('/friends/request', { receiverId: userId })
    return response.data
  },

  async acceptFriendRequest(friendshipId) {
    const response = await api.post(`/friends/accept/${friendshipId}`)
    return response.data
  },

  async declineFriendRequest(friendshipId) {
    const response = await api.post(`/friends/decline/${friendshipId}`)
    return response.data
  },

  async removeFriend(userId) {
    const response = await api.delete(`/friends/${userId}`)
    return response.data
  },

  async searchUsers(query) {
    const response = await api.get('/users/search', { params: { query } })
    return response.data
  }
}

export default api