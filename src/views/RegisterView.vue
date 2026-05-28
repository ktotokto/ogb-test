<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)
const error = ref('')

const handleRegister = async () => {
  error.value = ''
  
  if (!username.value || !email.value || !password.value) {
    error.value = 'Все поля обязательны для заполнения'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = 'Пароли не совпадают'
    return
  }
  
  if (password.value.length < 6) {
    error.value = 'Пароль должен быть не менее 6 символов'
    return
  }
  
  isSubmitting.value = true
  
  const success = await userStore.register(
    username.value,
    email.value,
    password.value
  )
  
  if (success) {
    // Редирект на главную или туда куда хотел пользователь
    const redirect = router.currentRoute.value.query.redirect || '/'
    await router.push(redirect)
  } else {
    error.value = userStore.error || 'Регистрация не удалась'
  }
  
  isSubmitting.value = false
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-white/10 p-8 shadow-2xl">
        <!-- Header -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent mb-2">
            Регистрация
          </h1>
          <p class="text-slate-400 text-sm">
            Создайте аккаунт для игры
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="error || userStore.error" class="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
          <p class="text-red-400 text-sm">{{ error || userStore.error }}</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleRegister" class="space-y-5">
          <!-- Username -->
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Имя пользователя
            </label>
            <input
              v-model="username"
              type="text"
              placeholder="Введите имя"
              class="w-full px-4 py-3 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all"
              :disabled="isSubmitting"
              required
            />
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Email
            </label>
            <input
              v-model="email"
              type="email"
              placeholder="your@email.com"
              class="w-full px-4 py-3 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all"
              :disabled="isSubmitting"
              required
            />
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Пароль
            </label>
            <input
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="w-full px-4 py-3 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all"
              :disabled="isSubmitting"
              required
            />
            <p class="text-xs text-slate-500 mt-1">Минимум 6 символов</p>
          </div>

          <!-- Confirm Password -->
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Подтвердите пароль
            </label>
            <input
              v-model="confirmPassword"
              type="password"
              placeholder="••••••••"
              class="w-full px-4 py-3 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all"
              :disabled="isSubmitting"
              required
            />
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isSubmitting"
            class="w-full py-3 px-4 bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-semibold rounded-xl shadow-lg shadow-violet-500/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:from-violet-600 disabled:hover:to-cyan-600"
          >
            {{ isSubmitting ? 'Регистрация...' : 'Зарегистрироваться' }}
          </button>
        </form>

        <!-- Login Link -->
        <div class="mt-6 text-center">
          <p class="text-slate-400 text-sm">
            Уже есть аккаунт?
            <router-link
              to="/login"
              class="text-violet-400 hover:text-violet-300 font-medium transition-colors"
            >
              Войти
            </router-link>
          </p>
        </div>
      </div>

      <!-- Footer -->
      <p class="text-center text-slate-500 text-xs mt-6">
        Регистрируясь, вы соглашаетесь с условиями использования
      </p>
    </div>
  </div>
</template>