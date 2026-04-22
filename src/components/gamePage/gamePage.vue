<script setup>
import { ref } from 'vue'
import GameHeader from './GameHeader.vue'
import GameMain from './gameMain/GameBoard.vue'
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

const handleZoomIn = () => {
  gameBoardRef.value?.zoomIn()
}

const handleZoomOut = () => {
  gameBoardRef.value?.zoomOut()
}

const handleResetZoom = () => {
  gameBoardRef.value?.resetZoom()
}

const handleSetTool = (tool) => {
  gameBoardRef.value?.setTool(tool)
}
</script>

<template>
  <div class="h-screen w-screen bg-slate-950 text-white flex flex-col overflow-hidden">

    <div class="flex-1 flex overflow-hidden">
      <aside :class="[
        'bg-slate-900/90 backdrop-blur border-r border-white/10 flex flex-col transition-all duration-300 overflow-y-auto',
        sidebarOpen ? 'w-80 translate-x-0' : 'w-0 -translate-x-full overflow-hidden'
      ]">
        <PlayersList />
        <GameTools />
        
      </aside>

      <main class="flex-1 relative bg-slate-950 overflow-hidden">
        <GameMain ref="gameBoardRef"  oncontextmenu="return false;" />
      </main>
    </div>
    <GameHeader :session-id="sessionId" @toggle-sidebar="sidebarOpen = !sidebarOpen" />

    <GameFooter @toggle-sidebar="sidebarOpen = !sidebarOpen" @zoom-in="handleZoomIn" @zoom-out="handleZoomOut"
      @reset-zoom="handleResetZoom" @set-tool="handleSetTool" />
  </div>
</template>