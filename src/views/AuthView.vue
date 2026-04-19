<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { toast } from 'vue-sonner'

const router = useRouter()
const userStore = useUserStore()

const isLogin = ref(true)
const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  try {
    if (isLogin.value) {
      await userStore.login(username.value, password.value)
      toast.success('Добро пожаловать!')
    } else {
      await userStore.register(username.value, email.value, password.value)
      toast.success('Аккаунт создан!')
    }
    router.push('/')
  } catch (e) {
    toast.error(e.message || 'Ошибка авторизации')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-center p-4">
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-violet-500/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-500/20 rounded-full blur-3xl"></div>
    </div>

    <div class="relative w-full max-w-md">
      <div class="bg-slate-900/80 backdrop-blur-xl rounded-3xl border border-white/10 p-8 shadow-2xl">
        <!-- Logo -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-cyan-500 mb-4">
            <span class="text-3xl">🎲</span>
          </div>
          <h1 class="text-2xl font-bold text-white">OGB Game</h1>
          <p class="text-slate-400 mt-1">Онлайн-платформа для настольных игр</p>
        </div>

        <!-- Tabs -->
        <div class="flex mb-6 bg-slate-800/50 rounded-xl p-1">
          <button @click="isLogin = true" :class="[
            'flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all',
            isLogin ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'
          ]">
            Вход
          </button>
          <button @click="isLogin = false" :class="[
            'flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all',
            !isLogin ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'
          ]">
            Регистрация
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Имя пользователя</label>
            <input v-model="username" type="text" required
              class="w-full px-4 py-3 rounded-xl bg-slate-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all"
              placeholder="player1" />
          </div>

          <div v-if="!isLogin">
            <label class="block text-sm font-medium text-slate-300 mb-2">Email</label>
            <input v-model="email" type="email" required
              class="w-full px-4 py-3 rounded-xl bg-slate-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all"
              placeholder="player@example.com" />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Пароль</label>
            <input v-model="password" type="password" required minlength="6"
              class="w-full px-4 py-3 rounded-xl bg-slate-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all"
              placeholder="Минимум 6 символов" />
          </div>

          <button type="submit" :disabled="loading"
            class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 text-white font-medium hover:from-violet-500 hover:to-cyan-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-violet-500/20">
            <span v-if="loading">Загрузка...</span>
            <span v-else>{{ isLogin ? 'Войти' : 'Создать аккаунт' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
