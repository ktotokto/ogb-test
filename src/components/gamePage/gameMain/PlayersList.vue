<script setup>
import { computed } from 'vue'

const props = defineProps({
    players: {
        type: Array,
        default: () => [
            { id: 1, name: 'Alex', role: 'creator', avatar: 'й', status: 'online', ready: true },
            { id: 2, name: 'Maria', role: 'admin', avatar: 'о', status: 'online', ready: true },
            { id: 3, name: 'John', role: 'guest', avatar: 'м', status: 'away', ready: false },
            { id: 4, name: 'Kate', role: 'guest', avatar: 'ф', status: 'offline', ready: false },
        ]
    }
})

const roleColors = {
    creator: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    admin: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
    guest: 'bg-slate-500/20 text-slate-400 border-slate-500/30'
}

const statusColors = {
    online: 'bg-emerald-500',
    away: 'bg-amber-500',
    offline: 'bg-slate-500'
}
</script>

<template>
    <div class="p-2 space-y-2">
        <div v-for="player in players" :key="player.id"
            class="flex items-center gap-3 p-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors group">
            <div class="relative">
                <div
                    class="w-10 h-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-600 flex items-center justify-center text-lg">
                    {{ player.avatar }}
                </div>
                <span class="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-slate-900"
                    :class="statusColors[player.status]" :title="player.status" />
            </div>

            <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                    <span class="font-medium truncate">{{ player.name }}</span>
                    <span class="px-2 py-0.5 text-xs rounded-full border" :class="roleColors[player.role]">
                        {{ player.role }}
                    </span>
                </div>
                <div class="flex items-center gap-2 mt-1">
                    <span class="text-xs" :class="player.ready ? 'text-emerald-400' : 'text-slate-500'">
                        {{ player.ready ? 'Готов' : 'Не готов' }}
                    </span>
                </div>
            </div>

            <div v-if="player.role === 'guest'" class="opacity-0 group-hover:opacity-100 transition-opacity">
                <button class="p-1.5 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                    </svg>
                </button>
            </div>
        </div>

        <button
            class="w-full mt-2 py-2.5 border-2 border-dashed border-slate-700 rounded-xl text-slate-400 hover:text-white hover:border-slate-500 hover:bg-slate-800/50 transition-all flex items-center justify-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Пригласить игрока
        </button>
    </div>
</template>