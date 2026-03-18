<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const time = ref(0)

const formattedTime = computed(() => {
    const hours = Math.floor(time.value / 3600)
    const minutes = Math.floor((time.value % 3600) / 60)
    const seconds = time.value % 60

    return {
        hours: String(hours).padStart(2, '0'),
        minutes: String(minutes).padStart(2, '0'),
        seconds: String(seconds).padStart(2, '0')
    }
})

let intervalId = null

onMounted(() => {
    intervalId = setInterval(() => {
        time.value++
    }, 1000)
})

onUnmounted(() => {
    if (intervalId) {
        clearInterval(intervalId)
    }
})

const emit = defineEmits(['save', 'invite', 'leave'])
</script>

<template>
    <nav
        class="w-full h-16 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-4 shrink-0">

        <div class="flex items-center gap-2 min-w-0">
            <svg class="w-5 h-5 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <span class="text-slate-300 font-mono text-sm truncate">Session #5F3-8DF-1XD</span>
        </div>

        <div class="flex items-center gap-1 px-4 py-2 bg-slate-800/50 rounded-xl border border-slate-700">
            <span class="text-2xl font-bold text-blue-400 font-mono">{{ formattedTime.hours }}</span>
            <span class="text-2xl font-bold text-slate-500">:</span>
            <span class="text-2xl font-bold text-blue-400 font-mono">{{ formattedTime.minutes }}</span>
            <span class="text-2xl font-bold text-slate-500">:</span>
            <span class="text-2xl font-bold text-blue-400 font-mono">{{ formattedTime.seconds }}</span>
        </div>

        <div class="flex items-center gap-2 shrink-0">
            <button @click="emit('save')"
                class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded-lg transition-colors text-sm">
                Save
            </button>
            <button @click="emit('invite')"
                class="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white font-medium rounded-lg transition-colors text-sm">
                Invite
            </button>
            <button @click="emit('leave')"
                class="px-4 py-2 bg-red-600/80 hover:bg-red-500 text-white font-medium rounded-lg transition-colors text-sm">
                Leave
            </button>
        </div>
    </nav>
</template>