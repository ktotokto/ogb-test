<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import {
  User, LogOut, Upload, Save, X, Settings,
  Image as ImageIcon, Edit3
} from 'lucide-vue-next'
import axios from 'axios'

const userStore = useUserStore()
const router = useRouter()

const isOpen = ref(false)
const isEditing = ref(false)
const isLoading = ref(false)

const currentUser = computed(() => userStore.currentUser)

const formData = ref({
  username: '',
  email: '',
  avatar_url: '',
  banner_url: '',
  bio: ''
})

onMounted(async () => {
  if (!currentUser.value) {
    await userStore.initAuth()
  }
})

const handleAvatarUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (event) => {
      formData.value.avatar_url = event.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleBannerUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (event) => {
      formData.value.banner_url = event.target.result

    }
    reader.readAsDataURL(file)
  }
}

const saveProfile = async () => {
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.put('/api/auth/user/profile', {
      username: formData.value.username,
      email: formData.value.email,
      avatar_url: formData.value.avatar_url,
      banner_url: formData.value.banner_url,
      bio: formData.value.bio
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    userStore.currentUser = response.data
    isEditing.value = false
    isOpen.value = false
  } catch (error) {
    alert('Ошибка: ' + (error.response?.data?.error || error.message))
  } finally {
    isLoading.value = false
  }
}

const logout = () => {
  userStore.logout()
}

const openEditor = () => {
  formData.value = {
    username: currentUser.value?.username || '',
    email: currentUser.value?.email || '',
    avatar_url: currentUser.value?.avatar_url || '',
    banner_url: currentUser.value?.banner_url || '',
    bio: currentUser.value?.bio || ''
  }
  isEditing.value = true
}


</script>

<template>
  <div class="relative">
    <button @click="isOpen = !isOpen"
      class="flex items-center gap-3 p-2 pr-4 hover:bg-slate-700 text-white rounded-2xl transition-all">
      <div
        class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center text-white font-bold overflow-hidden">
        <img v-if="currentUser?.avatar_url" :src="currentUser.avatar_url" class="w-full h-full object-cover" />
        <User v-else class="w-5 h-5" />
      </div>
      <span class="text-sm font-medium">{{ currentUser?.username }}</span>
    </button>

    <div v-if="isOpen"
      class="absolute top-12 right-0 w-80 bg-slate-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden z-50">
      <div class="relative h-24 bg-gradient-to-r from-slate-800 to-slate-900">
        <img v-if="currentUser?.banner_url" :src="currentUser.banner_url"
          class="w-full h-full object-cover opacity-60" />
      </div>

      <div class="px-4 relative -mt-8 mb-3 flex items-end gap-3">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br p-1 shadow-xl">
          <div class="w-full h-full rounded-full overflow-hidden bg-slate-800">
            <img v-if="currentUser?.avatar_url" :src="currentUser.avatar_url" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center">
              <User class="w-8 h-8 text-white opacity-50" />
            </div>
          </div>
        </div>
        <div class="pb-1">
          <h3 class="text-white font-bold text-lg leading-tight">{{ currentUser?.username }}</h3>
          <p class="text-slate-400 text-xs">{{ currentUser?.email }}</p>
        </div>
      </div>

      <div class="p-2 space-y-1 border-t border-white/5 bg-slate-900/50">
        <button @click="openEditor"
          class="w-full px-4 py-2 text-left text-sm text-slate-300 hover:bg-white/5 rounded-lg flex items-center gap-3 transition-all">
          <Settings class="w-4 h-4" />
          Редактировать профиль
        </button>
        <div class="border-t border-white/10 my-1"></div>
        <button @click="logout"
          class="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-red-500/10 rounded-lg flex items-center gap-3 transition-all">
          <LogOut class="w-4 h-4" />
          Выйти
        </button>
      </div>
    </div>

    <div v-if="isEditing" class="fixed pt-[45vh] inset-0 z-[60] flex items-center justify-center"
      @click.self="isEditing = false">
      <div class="bg-slate-900 border border-white/10 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        <div class="p-4 border-b border-white/10 flex justify-between items-center">
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <Edit3 class="w-4 h-4 text-violet-400" />
            Настройки профиля
          </h3>
          <button @click="isEditing = false" class="text-slate-400 hover:text-white">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="max-h-[70vh] overflow-y-auto p-6 space-y-5">
          <div class="space-y-2">
            <label class="text-xs font-semibold text-slate-400 uppercase">Баннер профиля</label>
            <div
              class="relative h-32 rounded-xl overflow-hidden bg-slate-800 border border-white/10 group cursor-pointer hover:border-violet-500/50 transition-all">
              <img v-if="formData.banner_url" :src="formData.banner_url" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center text-slate-500 bg-slate-800/50">
                <span class="text-xs">Нет баннера</span>
              </div>
              <div
                class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 text-white text-xs font-medium">
                <ImageIcon class="w-4 h-4" /> Изменить
              </div>
              <input type="file" accept="image/*" @change="handleBannerUpload" class="hidden" />
            </div>
          </div>

          <div class="flex items-center gap-4">
            <label class="relative cursor-pointer group">
              <div class="w-20 h-20 rounded-full bg-gradient-to-br p-1 shadow-lg">
                <div class="w-full h-full rounded-full overflow-hidden bg-slate-800">
                  <img v-if="formData.avatar_url" :src="formData.avatar_url" class="w-full h-full object-cover" />
                  <User v-else class="w-full h-full p-4 text-white opacity-50" />
                </div>
              </div>
              <div
                class="absolute inset-0 bg-black/40 rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <Upload class="w-5 h-5 text-white" />
              </div>
              <input type="file" accept="image/*" @change="handleAvatarUpload" class="hidden" />
            </label>
            <div>
              <p class="text-white font-medium">Ваш аватар</p>
              <p class="text-xs text-slate-500">JPG или PNG, макс 2MB</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-xs font-semibold text-slate-400 uppercase">Имя пользователя</label>
              <input v-model="formData.username" type="text"
                class="w-full px-4 py-2.5 bg-slate-800 border border-white/10 rounded-lg text-white focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all" />
            </div>

            <div class="space-y-2">
              <label class="text-xs font-semibold text-slate-400 uppercase">Email</label>
              <input v-model="formData.email" type="email"
                class="w-full px-4 py-2.5 bg-slate-800 border border-white/10 rounded-lg text-white focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all" />
            </div>

            <div class="space-y-2">
              <label class="text-xs font-semibold text-slate-400 uppercase">О себе</label>
              <textarea v-model="formData.bio" rows="3" placeholder="Расскажите немного о себе..."
                class="w-full px-4 py-2.5 bg-slate-800 border border-white/10 rounded-lg text-white focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all resize-none"></textarea>
            </div>
          </div>

          <div class="flex gap-3 pt-2">
            <button @click="isEditing = false"
              class="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors">
              Отмена
            </button>
            <button @click="saveProfile" :disabled="isLoading"
              class="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-all">
              <Save class="w-4 h-4" />
              {{ isLoading ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>