<script setup>
import { ref, nextTick } from 'vue'
import GameHeader from './GameHeader.vue'
import GameMain from './gameMain/GameBoard.vue'
import GameHand from './GameHand.vue'
import GameFooter from './GameFooter.vue'
import PlayersList from './gameMain/PlayersList.vue'
import GameTools from './gameMain/GameTools.vue'

defineProps({
  sessionId: {
    type: String,
    required: true
  }
})

const sidebarOpen = ref(true)
const gameBoardRef = ref(null)

// ✅ Безопасные хендлеры с проверкой
const handleZoomIn = () => {
  if (gameBoardRef.value?.zoomIn) {
    gameBoardRef.value.zoomIn()
  }
}

const handleZoomOut = () => {
  if (gameBoardRef.value?.zoomOut) {
    gameBoardRef.value.zoomOut()
  }
}

const handleResetZoom = () => {
  if (gameBoardRef.value?.resetZoom) {
    gameBoardRef.value.resetZoom()
  }
}

const handlePanMode = (enabled) => {
  // Можно добавить логику переключения режима панорамирования
  console.log('Pan mode:', enabled)
}
</script>

<template>
  <div class="h-screen w-screen bg-slate-950 text-white flex flex-col overflow-hidden">
    <GameHeader :session-id="sessionId" />

    <div class="flex-1 flex overflow-hidden">
      <aside :class="[
        'glass-strong border-r border-white/10 flex flex-col transition-all duration-300 overflow-y-auto',
        sidebarOpen ? 'w-80 translate-x-0' : 'w-0 -translate-x-full overflow-hidden'
      ]">
        <PlayersList />
        <GameTools />
      </aside>

      <main class="flex-1 relative bg-slate-950 overflow-hidden">
        <GameMain ref="gameBoardRef" />
        <GameHand />
      </main>
    </div>

    <GameFooter @toggle-sidebar="sidebarOpen = !sidebarOpen" @zoom-in="handleZoomIn" @zoom-out="handleZoomOut"
      @reset-zoom="handleResetZoom" @pan-mode="handlePanMode" />
  </div>
</template>