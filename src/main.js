import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Инициализация: если есть токен, восстанавливаем пользователя
import { useUserStore } from '@/stores/user'
import { useSocket } from '@/composables/useSocket'

const token = localStorage.getItem('accessToken')
if (token) {
  const userStore = useUserStore(pinia)
  userStore.fetchCurrentUser().catch(() => {
    // Если токен невалидный — очищаем
    localStorage.removeItem('accessToken')
  })
}

app.mount('#app')
