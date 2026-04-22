import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/game/:sessionId',
    name: 'Game',
    component: () => import('@/views/GameView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/friends',
    name: 'Friends',
    component: () => import('@/views/FriendsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/games',
    name: 'SavedGames',
    component: () => import('@/views/FriendsView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// ✅ Router guard
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth

  // Если страница требует авторизации
  if (requiresAuth && !userStore.isAuthenticated) {
    // Сохраняем куда хотел попасть пользователь
    next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  // Если пользователь уже авторизован и идёт на вход — редирект на главную
  else if (!requiresAuth && userStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Home' })
  }
  // Во всех остальных случаях — разрешаем
  else {
    next()
  }
})

export default router