<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { LogOut, User, Gamepad2, Users } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()

const isAuthenticated = computed(() => userStore.isAuthenticated)
const currentUser = computed(() => userStore.currentUser)

const handleLogout = () => {
  userStore.logout()
  router.push('/')
}
</script>

<template>
  <header class="w-full bg-slate-900/90 backdrop-blur border-b border-white/10 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-2 group">
        <Gamepad2 class="w-8 h-8 text-violet-400 group-hover:text-violet-300 transition-colors" />
        <span class="text-xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
          OGB
        </span>
      </router-link>

      <!-- Navigation -->
      <nav class="flex items-center gap-4">
        <template v-if="isAuthenticated">
          <router-link
            to="/games"
            class="px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all flex items-center gap-2"
          >
            <Gamepad2 class="w-4 h-4" />
            Мои игры
          </router-link>
          
          <router-link
            to="/friends"
            class="px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all flex items-center gap-2"
          >
            <Users class="w-4 h-4" />
            Друзья
          </router-link>

          <div class="flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 rounded-lg">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center">
              <User class="w-4 h-4 text-white" />
            </div>
            <span class="text-sm font-medium text-slate-200 hidden md:block">
              {{ currentUser?.username }}
            </span>
          </div>

          <button
            @click="handleLogout"
            class="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
            title="Выйти"
          >
            <LogOut class="w-5 h-5" />
          </button>
        </template>

        <template v-else>
          <router-link
            to="/login"
            class="px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all"
          >
            Войти
          </router-link>
          
          <router-link
            to="/register"
            class="px-4 py-2 text-sm bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white rounded-lg transition-all shadow-lg shadow-violet-500/25"
          >
            Регистрация
          </router-link>
        </template>
      </nav>
    </div>
  </header>
</template>