<script setup lang="ts">
import { computed, ref } from 'vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { Crown, Star, User } from 'lucide-vue-next'
import type { Player, AvatarItem } from '@/types/index'

const gameStore = useGameStore()
const userStore = useUserStore()

const players = computed(() => gameStore.players || [])
const players_avatars = ref<AvatarItem[]>([])

const getAvatar = async (player: Player) => {  
  const user = await userStore.fetchUserById(player.user_id)
  return user.avatar_url
}

players.value.forEach(element => {
  getAvatar(element).then(url => {
    players_avatars.value.push({
      userId: element.user_id,
      url: url
    })
  })
})

const currentUserId = computed(() => userStore.userId)

const isMe = (player: Player) => {
  return player.user_id === currentUserId.value ||
    player.user?.id === currentUserId.value ||
    player.id === currentUserId.value
}

const roleConfig = {
  creator: {
    icon: Crown,
    color: 'from-amber-400 to-orange-500',
    bg: 'bg-amber-500/20',
    text: 'text-amber-400',
    border: 'border-amber-500/30',
    label: 'Создатель'
  },
  admin: {
    icon: Star,
    color: 'from-violet-400 to-purple-500',
    bg: 'bg-violet-500/20',
    text: 'text-violet-400',
    border: 'border-violet-500/30',
    label: 'Админ'
  },
  player: {
    icon: User,
    color: 'from-slate-400 to-slate-500',
    bg: 'bg-slate-500/20',
    text: 'text-slate-400',
    border: 'border-slate-500/30',
    label: 'Игрок'
  },
  guest: {
    icon: User,
    color: 'from-slate-400 to-slate-500',
    bg: 'bg-slate-500/20',
    text: 'text-slate-400',
    border: 'border-slate-500/30',
    label: 'Гость'
  }
}

const statusConfig = {
  online: { color: 'bg-emerald-400', glow: 'shadow-[0_0_10px_rgba(16,185,129,0.5)]', label: 'Онлайн' },
  away: { color: 'bg-amber-400', glow: '', label: 'Отошёл' },
  offline: { color: 'bg-slate-500', glow: '', label: 'Оффлайн' },
  unknown: { color: 'bg-slate-600', glow: '', label: 'Неизвестно' }
}

const getName = (player: Player) => {
  return player.user.username
}

const getStatus = (player: Player) => {
  if (player.user?.is_online !== undefined) return player.user.is_online ? 'online' : 'offline'
  return 'online'
}

const getRole = (player: Player) => {
  return player.role as keyof typeof roleConfig
}
</script>

<template>
  <div class="w-95 p-6 border-b border-white/10">
    <h2 class="font-bold text-lg mb-5 flex items-center gap-2">
      <span class="w-1 h-6 bg-gradient-to-b from-violet-500 to-cyan-500 rounded-full"></span>
      Игроки
      <span class="text-xs px-2 py-1 rounded-full glass text-slate-400">{{ players.length }}</span>
    </h2>

    <div v-if="players.length === 0" class="text-center py-8 text-slate-500 text-sm">
      Пока нет игроков
    </div>

    <div v-else class="space-y-3">
      <div v-for="player in players" :key="player.user_id || player.id"
        class="pb-3 group p-4 rounded-xl glass-light hover:bg-white/5 transition-all duration-300 border border-transparent"
        :class="[
          isMe(player)
            ? 'border-violet-500/50 bg-violet-500/5 ring-1 ring-violet-500/30'
            : 'hover:border-violet-500/30'
        ]">

        <div class="flex items-center gap-3">
          <div class="relative">
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold shadow-lg group-hover:scale-110 transition-transform overflow-hidden"
              :class="[
                isMe(player)
                  ? 'bg-gradient-to-br from-violet-500 to-cyan-500 text-white ring-2 ring-violet-400/50'
                  : 'bg-gradient-to-br from-slate-700 to-slate-800 text-slate-300'
              ]">
              <img v-if="players_avatars.find(a => a.userId === player.user_id)?.url"
                :src="players_avatars.find(a => a.userId === player.user_id)?.url"
                class="w-full h-full object-cover rounded-xl" />
              <span v-else>
                {{ player.user.username.substring(0, 2).toUpperCase() || '??' }}
              </span>

            </div>

            <div v-if="isMe(player)"
              class="absolute -top-1 -left-1 px-1.5 py-0.5 bg-violet-600 text-white text-[10px] font-bold rounded-full shadow-lg whitespace-nowrap">
              Это вы
            </div>
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-semibold text-sm truncate" :class="isMe(player) ? 'text-violet-300' : 'text-white'">
                {{ getName(player) }}
                <span v-if="isMe(player)" class="text-xs text-violet-400/70">(вы)</span>
              </span>
              <component :is="roleConfig[getRole(player)]?.icon || roleConfig.player.icon" class="w-4 h-4 flex-shrink-0"
                :class="roleConfig[getRole(player)]?.text || roleConfig.player.text"
                :title="roleConfig[getRole(player)]?.label || 'Игрок'" />
            </div>

            <div class="flex items-center gap-2 text-xs">
              <span :class="statusConfig[getStatus(player)].label">
                {{ statusConfig[getStatus(player)].label }}
              </span>

              <span v-if="player.joined_at" class="text-slate-600">•</span>

              <span v-if="player.joined_at" class="text-slate-500">
                {{ new Date(player.joined_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) }}
              </span>
            </div>
          </div>

          <div class="px-3 py-1.5 rounded-lg text-xs font-semibold glass capitalize flex items-center gap-1" :class="[
            roleConfig[getRole(player)]?.bg || roleConfig.player.bg,
            roleConfig[getRole(player)]?.text || roleConfig.player.text,
            roleConfig[getRole(player)]?.border || roleConfig.player.border
          ]">
            <component :is="roleConfig[getRole(player)]?.icon || roleConfig.player.icon" class="w-3 h-3" />
            {{ roleConfig[getRole(player)]?.label || 'Игрок' }}
          </div>
        </div>

        <div v-if="isMe(player)"
          class="absolute left-0 top-4 bottom-4 w-1 bg-gradient-to-b from-violet-500 to-cyan-500 rounded-r-full">
        </div>
      </div>
    </div>

    <button v-if="gameStore.isAdmin"
      class="w-full mt-5 py-3.5 rounded-xl border-2 border-dashed border-violet-500/30 hover:border-violet-500/60 text-violet-400 hover:text-violet-300 hover:bg-violet-500/5 transition-all duration-300 flex items-center justify-center gap-2 group font-medium"
      @click="$emit('invite')">
      <span class="text-xl group-hover:rotate-90 transition-transform">+</span>
      <span>Пригласить игрока</span>
    </button>

    <div v-else-if="players.length > 0" class="mt-5 text-center text-xs text-slate-500">
      Только создатель может приглашать
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse-online {

  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: 0.7;
    transform: scale(0.9);
  }
}

.bg-emerald-400 {
  animation: pulse-online 2s ease-in-out infinite;
}

.ring-violet-500\/30 {
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.15);
}
</style>