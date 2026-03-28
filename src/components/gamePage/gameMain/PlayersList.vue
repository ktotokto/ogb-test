<script setup>
import { ref } from 'vue'
import { Crown, Star, User, Wifi, WifiOff } from 'lucide-vue-next'

const players = ref([
  { id: 1, name: 'Alex', role: 'creator', avatar: '1', status: 'online', score: 1250 },
  { id: 2, name: 'Maria', role: 'admin', avatar: '2', status: 'online', score: 980 },
  { id: 3, name: 'John', role: 'guest', avatar: '3', status: 'away', score: 750 },
  { id: 4, name: 'Kate', role: 'guest', avatar: '4', status: 'offline', score: 540 }
])

const roleConfig = {
  creator: { icon: Crown, color: 'from-amber-400 to-orange-500', bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/30' },
  admin: { icon: Star, color: 'from-violet-400 to-purple-500', bg: 'bg-violet-500/20', text: 'text-violet-400', border: 'border-violet-500/30' },
  guest: { icon: User, color: 'from-slate-400 to-slate-500', bg: 'bg-slate-500/20', text: 'text-slate-400', border: 'border-slate-500/30' }
}

const statusConfig = {
  online: { color: 'bg-emerald-400', text: 'text-emerald-400', label: 'Онлайн' },
  away: { color: 'bg-amber-400', text: 'text-amber-400', label: 'Отошёл' },
  offline: { color: 'bg-slate-500', text: 'text-slate-500', label: 'Оффлайн' }
}
</script>

<template>
  <div class="w-80 p-6 border-b border-white/10">
    <h2 class="font-bold text-lg mb-5 flex items-center gap-2">
      <span class="w-1 h-6 bg-gradient-to-b from-violet-500 to-cyan-500 rounded-full"></span>
      Игроки
      <span class="text-xs px-2 py-1 rounded-full glass text-slate-400">{{ players.length }}</span>
    </h2>
    
    <div class="space-y-3">
      <div v-for="player in players" :key="player.id" 
           class="pb-8 group p-4 rounded-xl glass-light hover:bg-white/5 transition-all duration-300 border border-transparent hover:border-violet-500/30 cursor-pointer">
        <div class="flex items-center gap-3">
          <!-- Avatar -->
          <div class="relative">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center text-2xl shadow-lg group-hover:scale-110 transition-transform">
              {{ player.avatar }}
            </div>
            <div class="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full border-2 border-slate-900" 
                 :class="statusConfig[player.status].color"></div>
          </div>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-semibold text-sm truncate">{{ player.name }}</span>
              <component :is="roleConfig[player.role].icon" 
                        class="w-4 h-4 flex-shrink-0" 
                        :class="roleConfig[player.role].text" />
            </div>
            <div class="flex items-center gap-2 text-xs">
              <span :class="statusConfig[player.status].text">{{ statusConfig[player.status].label }}</span>
              <span class="text-slate-600">•</span>
              <span class="text-slate-400">{{ player.score }} pts</span>
            </div>
          </div>

          <!-- Role Badge -->
          <div class="px-3 py-1.5 rounded-lg text-xs font-semibold glass capitalize" 
               :class="[roleConfig[player.role].bg, roleConfig[player.role].text, roleConfig[player.role].border]">
            {{ player.role }}
          </div>
        </div>
      </div>
    </div>

    <!-- Invite Button -->
    <button class="w-full mt-5 py-3.5 rounded-xl border-2 border-dashed border-violet-500/30 hover:border-violet-500/60 text-violet-400 hover:text-violet-300 hover:bg-violet-500/5 transition-all duration-300 flex items-center justify-center gap-2 group font-medium">
      <span class="text-xl group-hover:rotate-90 transition-transform">+</span>
      <span>Пригласить игрока</span>
    </button>
  </div>
</template>