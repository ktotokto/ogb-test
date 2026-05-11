<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useGameStore } from '@/stores/game'
import { Gamepad2, Sparkles, Users, Zap, LogOut, User, Plus, Search } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()
const gameStore = useGameStore()

const isLoading = ref(false)
const error = ref(null)

const isAuthenticated = computed(() => userStore.isAuthenticated)


const joinGameById = async () => {
  if (!isAuthenticated.value) {
    router.push('/login?redirect=/')
    return
  }

  const sessionId = prompt('Введите ID игры:')
  if (!sessionId) return

  isLoading.value = true
  error.value = null

  try {
    const session = await gameStore.joinSession(sessionId)
    if (session?.id) {
      router.push(`/game/${session.id}`)
    }
  } catch (err) {
    console.error('Failed to join game:', err)
    alert(err.response?.data?.error || 'Не удалось присоединиться к игре')
  } finally {
    isLoading.value = false
  }
}


const goToLogin = () => router.push('/login')
const goToRegister = () => router.push('/register')

const features = [
  { icon: Gamepad2, title: 'Играй онлайн', desc: 'Создавай игровые сессии' },
  { icon: Users, title: 'Играй с друзьями', desc: 'Приглашай до 8 игроков' },
  { icon: Zap, title: 'Быстро и удобно', desc: 'Мгновенная синхронизация' },
  { icon: Sparkles, title: 'Кастомизация', desc: 'Свои правила и объекты' }
]

onMounted(() => {
  if (!userStore.currentUser && userStore.token) {
    userStore.fetchProfile()
  }
})
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex flex-col relative overflow-hidden">
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"
        style="animation-delay: 1s;"></div>
    </div>

    <main class="flex-1 flex items-center justify-center relative z-10 px-6 py-12">
      <div class="max-w-6xl w-full">

        <div class="text-center mb-16">
          <div
            class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/50 border border-white/10 mb-6">
            <Sparkles class="w-4 h-4 text-violet-400" />
            <span class="text-sm text-slate-300">Онлайн игровая платформа</span>
          </div>

          <h1 class="text-6xl md:text-7xl font-bold mb-6">
            <span
              class="bg-gradient-to-r from-violet-400 via-cyan-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
              OGB
            </span>
          </h1>

          <p class="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
            Играй в настольные игры онлайн с друзьями в реальном времени.
            Создавай свои правила, карты и наслаждайся игрой.
          </p>

          <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
            <template v-if="isAuthenticated">
              <router-link to="/games">
                <button :disabled="isLoading"
                  class="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-semibold rounded-xl shadow-lg shadow-violet-500/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 group">
                  <Plus class="w-5 h-5 group-hover:rotate-90 transition-transform" />
                  <span>{{ isLoading ? 'Создание...' : 'Создать игру' }}</span>
                </button>
              </router-link>


              <button @click="joinGameById" :disabled="isLoading"
                class="w-full sm:w-auto px-8 py-4 bg-slate-800/50 hover:bg-slate-700/50 border border-white/10 text-white font-semibold rounded-xl transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2">
                <Search class="w-5 h-5" />
                <span>Присоединиться</span>
              </button>
            </template>

            <template v-else>
              <button @click="goToRegister"
                class="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-semibold rounded-xl shadow-lg shadow-violet-500/25 transition-all duration-300 flex items-center justify-center gap-3">
                <Sparkles class="w-5 h-5" />
                <span>Начать бесплатно</span>
              </button>

              <button @click="goToLogin"
                class="w-full sm:w-auto px-8 py-4 bg-slate-800/50 hover:bg-slate-700/50 border border-white/10 text-white font-semibold rounded-xl transition-all duration-300">
                Войти в аккаунт
              </button>
            </template>
          </div>

          <p v-if="error" class="mt-4 text-red-400 text-sm">
            {{ error }}
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="(feature, index) in features" :key="index"
            class="p-6 bg-slate-900/50 backdrop-blur border border-white/10 rounded-2xl text-center group hover:border-violet-500/50 transition-all duration-300">
            <div
              class="w-14 h-14 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-violet-500/20 to-cyan-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
              <component :is="feature.icon" class="w-7 h-7 text-violet-400" />
            </div>
            <h3 class="font-bold text-lg mb-2 text-white">{{ feature.title }}</h3>
            <p class="text-sm text-slate-400">{{ feature.desc }}</p>
          </div>
        </div>

      </div>
    </main>

    <footer class="w-full p-6 text-center text-slate-500 text-sm border-t border-white/5">
      <p>© 2026 OGB — Онлайн игровая платформа</p>
    </footer>
  </div>
</template>

<style scoped>
@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

.animate-gradient {
  animation: gradient 3s ease infinite;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}
</style>