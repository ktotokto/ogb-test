<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Gamepad2, Sparkles, Users, Zap, LogOut, User } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()

const createGame = async () => {
  if (!userStore.isAuthenticated) {
    router.push('/auth')
    return
  }

  const gameStore = (await import('@/stores/game')).useGameStore()
  const session = await gameStore.createSession('Моя игра')
  router.push(`/game/${session.id}`)
}

const logout = () => {
  userStore.logout()
  router.push('/')
}

const features = [
  { icon: Gamepad2, title: 'Играй онлайн', desc: 'Создавай игровые сессии' },
  { icon: Users, title: 'Играй с друзьями', desc: 'Приглашай до 1 игрока' },
  { icon: Zap, title: 'Быстро и удобно', desc: 'Мгновенная синхронизация' },
  { icon: Sparkles, title: 'Кастомизация', desc: 'Свои правила и объекты' }
]
</script>

<template>
  <div class="min-h-screen gradient-bg particle-bg flex items-center justify-center relative overflow-hidden">
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-violet-500/20 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
    </div>

    <div class="relative z-10 max-w-6xl mx-auto px-6">
      <div class="text-center mb-16 animate-slide-in">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6 animate-float">
          <Sparkles class="w-4 h-4 text-violet-400" />
          <span class="text-sm text-slate-300">Онлайн игровая платформа</span>
        </div>
        
        <h1 class="text-7xl font-bold mb-6">
          <span class="gradient-text">OGB</span>
        </h1>
        <p class="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
          Играй в настольные игры онлайн с друзьями в реальном времени. 
          Создавай свои правила и наслаждайся игрой.
        </p>
        
        <div class="flex items-center justify-center gap-4">
          <button @click="createGame" 
                  class="btn-primary text-lg px-8 py-4 flex items-center gap-3 group">
            <Gamepad2 class="w-5 h-5 group-hover:rotate-12 transition-transform" />
            <span>Создать игру</span>
            <Sparkles class="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>
          
          <button class="px-8 py-4 rounded-xl font-semibold glass hover:bg-white/10 transition-all duration-300 text-slate-300 hover:text-white">
            Как это работает?
          </button>
        </div>
      </div>

      <div class="grid md:grid-cols-4 gap-6 mt-20">
        <div v-for="(feature, index) in features" :key="index"
             class="card-glass p-6 text-center group hover:scale-105 transition-all duration-300">
          <div class="w-14 h-14 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-violet-500/20 to-cyan-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
            <component :is="feature.icon" class="w-7 h-7 text-violet-400" />
          </div>
          <h3 class="font-bold text-lg mb-2 text-white">{{ feature.title }}</h3>
          <p class="text-sm text-slate-400">{{ feature.desc }}</p>
        </div>
      </div>
    </div>
  </div>
</template>