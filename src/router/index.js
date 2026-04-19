import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/views/AuthView.vue')
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/game/:sessionId',
    name: 'Game',
    component: () => import('@/views/GameView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Навигационный guard
router.beforeEach(async (to) => {
  const token = localStorage.getItem('accessToken')

  // Если есть токен и идёт на /auth — редирект на главную
  if (to.name === 'Auth' && token) {
    return { name: 'Home' }
  }

  // Если нет токена и идёт на GameView — можно без авторизации (для быстрого теста)
  // В продакшене здесь будет проверка авторизации
})

export default router
