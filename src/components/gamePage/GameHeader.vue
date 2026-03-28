<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Clock, Save, UserPlus, LogOut, Wifi, WifiOff } from 'lucide-vue-next'

const props = defineProps({
  sessionId: String
})

const time = ref(0)
const isConnected = ref(true)

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
  intervalId = setInterval(() => time.value++, 1000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>

<template>
  <nav class="h-20 glass-strong border-b border-white/10 flex items-center justify-between px-8 shrink-0 relative overflow-hidden">
    <div class="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
    
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-3 px-5 py-2.5 rounded-xl glass-light border border-white/10">
        <div class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.8)]"></div>
        <span class="copy font-mono text-sm font-semibold text-slate-300">#{{ sessionId }}</span>
      </div>
    </div>

    <div class="flex items-center gap-3 px-8 py-3 rounded-2xl glass bg-gradient-to-br from-violet-500/10 to-cyan-500/10 border border-violet-500/30 shadow-lg">
      <Clock class="w-5 h-5 text-violet-400" />
      <div class="flex items-center gap-1.5 font-mono text-2xl font-bold">
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-400 min-w-[40px] text-center">
          {{ formattedTime.hours }}
        </span>
        <span class="text-slate-500">:</span>
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-400 min-w-[40px] text-center">
          {{ formattedTime.minutes }}
        </span>
        <span class="text-slate-500">:</span>
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400 min-w-[40px] text-center">
          {{ formattedTime.seconds }}
        </span>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <button class="btn-primary flex items-center gap-2.5 px-6">
        <Save class="w-4 h-4" />
        <span class="font-medium">Сохранить</span>
      </button>
      <button class="btn-secondary flex items-center gap-2.5 px-6">
        <UserPlus class="w-4 h-4" />
        <span class="font-medium">Пригласить</span>
      </button>
      <button class="px-6 py-2.5 rounded-xl font-semibold transition-all duration-300 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 hover:border-red-500/50 flex items-center gap-2.5">
        <LogOut class="w-4 h-4" />
        <span class="font-medium">Выйти</span>
      </button>
    </div>
  </nav>
</template>