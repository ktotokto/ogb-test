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
    path: '/games',
    name: 'SavedGames',
    component: () => import('@/views/GameListView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth

  if (!userStore.isAuthChecked) {
    try {
      await userStore.initAuth()
    } catch (err) {
      console.error('Auth init failed:', err)
    }
  }

  if (requiresAuth && !userStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  else if (!requiresAuth && userStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Home' })
  }
  else {
    next()
  }
})

export default router