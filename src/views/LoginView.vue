<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Gamepad2, Sparkles } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const isSubmitting = ref(false)
const showPassword = ref(false)

const handleLogin = async () => {
  isSubmitting.value = true
  const success = await userStore.login(username.value, password.value)
  
  if (success) {
    const redirect = router.currentRoute.value.query.redirect || '/'
    await router.push(redirect)
  }
  isSubmitting.value = false
}

const goToRegister = () => router.push('/register')
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-center px-4 relative overflow-hidden">
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
    </div>

    <div class="relative z-10 w-full max-w-md">
      <div class="text-center mb-8">
        <div class="inline-flex items-center gap-2 mb-4">
          <Gamepad2 class="w-10 h-10 text-violet-400" />
          <span class="text-2xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
            OGB
          </span>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">Вход в аккаунт</h1>
        <p class="text-slate-400">Добро пожаловать обратно!</p>
      </div>

      <div class="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-white/10 p-8 shadow-2xl shadow-violet-500/10">
        <div v-if="userStore.error" class="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start gap-3">
          <span class="text-red-400 text-sm flex-1">{{ userStore.error }}</span>
          <button @click="userStore.error = null" class="text-red-400 hover:text-red-300 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Имя пользователя
            </label>
            <div class="relative">
              <input
                v-model="username"
                type="text"
                placeholder="Введите имя"
                class="w-full px-4 py-3 pl-10 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all disabled:opacity-50"
                :disabled="isSubmitting"
                required
                autocomplete="username"
              />
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Пароль
            </label>
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                class="w-full px-4 py-3 pl-10 pr-10 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all disabled:opacity-50"
                :disabled="isSubmitting"
                required
                autocomplete="current-password"
              />
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
              >
                <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
          </div>

          <div class="flex items-center justify-between text-sm">
            <label class="flex items-center gap-2 text-slate-400 cursor-pointer">
              <input type="checkbox" class="w-4 h-4 rounded border-slate-600 bg-slate-800 text-violet-500 focus:ring-violet-500/20" />
              <span>Запомнить меня</span>
            </label>
            <a href="#" class="text-violet-400 hover:text-violet-300 transition-colors">
              Забыли пароль?
            </a>
          </div>

          <button
            type="submit"
            :disabled="isSubmitting"
            class="w-full py-3 px-4 bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-semibold rounded-xl shadow-lg shadow-violet-500/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:from-violet-600 disabled:hover:to-cyan-600 flex items-center justify-center gap-2 group"
          >
            <Sparkles v-if="!isSubmitting" class="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
            <span>{{ isSubmitting ? 'Вход...' : 'Войти' }}</span>
            <svg v-if="!isSubmitting" class="w-4 h-4 opacity-0 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </form>

        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-white/10"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-4 bg-slate-900 text-slate-500">или</span>
          </div>
        </div>

        <div class="text-center">
          <p class="text-slate-400 text-sm">
            Нет аккаунта?
            <button @click="goToRegister" class="text-violet-400 hover:text-violet-300 font-medium transition-colors">
              Зарегистрироваться
            </button>
          </p>
        </div>
      </div>

      <p class="text-center text-slate-500 text-xs mt-6">
        Нажимая "Войти", вы соглашаетесь с условиями использования
      </p>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

input::-webkit-scrollbar {
  width: 6px;
}

input::-webkit-scrollbar-track {
  background: transparent;
}

input::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.5);
  border-radius: 3px;
}

input::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.7);
}

input:focus {
  animation: focusPulse 0.3s ease;
}

@keyframes focusPulse {
  0% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0); }
  50% { box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2); }
  100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0); }
}

button[type="submit"]:hover {
  box-shadow: 0 0 30px rgba(139, 92, 246, 0.4), 0 0 60px rgba(6, 182, 212, 0.2);
}
</style>