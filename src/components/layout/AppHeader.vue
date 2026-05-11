<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Gamepad2 } from 'lucide-vue-next'
import UserProfile from './UserProfile.vue'

const router = useRouter()
const userStore = useUserStore()

const isAuthenticated = computed(() => userStore.isAuthenticated)

</script>

<template>
  <header class="w-full bg-slate-900/90 backdrop-blur border-b border-white/10 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <router-link to="/" class="flex items-center gap-2 group">
        <span class="text-xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
          OGB
        </span>
      </router-link>

      <nav class="flex items-center gap-4">
        <template v-if="isAuthenticated">
          <router-link
            to="/games"
            class="px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all flex items-center gap-2"
          >
            <Gamepad2 class="w-4 h-4" />
            Мои игры
          </router-link>
          
          <UserProfile />
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