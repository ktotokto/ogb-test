<script setup>
import { computed, ref } from 'vue'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'

const gameStore = useGameStore()
const userStore = useUserStore()

const isDisplay = ref(true)

const props = defineProps({
  objects: Array
});

const getObjectIcon = (type) => {
  const icons = {
    card: '🎴',
    dice: '🎲',
    token: '🔵',
    model: '🎭',
    image: '🖼️',
    text: '📝'
  }
  return icons[type] || '📦'
}

const returnToBoard = (object) => {
  console.log("Да");

  // gameStore.updateObject(object.id, { inHand: false })

  // const { useGameWebSocket } = await import('@/composables/useGameWebSocket')
  // const { socket } = useGameWebSocket()
  // if (socket.value && gameStore.sessionId) {
  //   socket.value.emit('object:sync', {
  //     sessionId: gameStore.sessionId,
  //     userId: userStore.userId,
  //     update: {
  //       objectId: object.id,
  //       changes: { inHand: false },
  //       type: 'hand-return'
  //     }
  //   })
  // }
}



</script>
<!-- 
<template>
  <div class="hand">
    <div v-for="object in objects" :key="object.id" class="object-card">
      {{ object.label }}
    </div>
  </div>
</template> -->


<template>
  <div v-if="isDisplay" class="hand-container">
    <div class="hand-header">
      <div class="flex items-center gap-2">
        <span class="hand-title">Рука</span>
        <span class="hand-count">{{ objects.length }}</span>
      </div>
    </div>

    <div v-if="!objects || objects.length === 0" class="hand-empty">
      <span class="hand-empty-text">Рука пуста</span>
    </div>

    <div v-else class="hand-cards">
      <div v-for="object in objects" :key="object.id" class="hand-card" @click="returnToBoard(object)">
        <div class="hand-card-inner">
          <div class="hand-card-media">
            <template v-if="object.cardData?.frontImage">
              <img :src="object.cardData.frontImage" class="hand-card-image" draggable="false" />
            </template>
            <template v-else>
              <span class="hand-card-icon">{{ getObjectIcon(object.type) }}</span>
            </template>
          </div>

          <div class="hand-card-info">
            <span class="hand-card-label">{{ object.label || 'Карта' }}</span>
            <span class="hand-card-type">{{ object.type || 'card' }}</span>
          </div>

          <div class="hand-card-action">
            <button @click="returnToBoard" class="action-text">← На поле</button>
          </div>
        </div>
      </div>
    </div>
    <div class="hand-footer">
      <button @click="!isDisplay" class="footer-text">Скрыть руку</button>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.hand-container {
  @apply absolute bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3 max-w-[90%] w-auto;
  z-index: 40;
}

.hand-header {
  @apply px-4 py-2 rounded-xl bg-slate-800/60 backdrop-blur-md border border-white/10 shadow-lg;
}

.hand-icon {
  @apply text-xl;
}

.hand-title {
  @apply text-sm font-semibold text-white;
}

.hand-count {
  @apply px-2 py-0.5 text-xs font-bold bg-violet-600/80 text-white rounded-full;
}

.hand-empty {
  @apply flex flex-col items-center gap-2 px-8 py-6 rounded-2xl bg-slate-800/40 backdrop-blur-md border border-white/5 shadow-xl;
}

.hand-empty-icon {
  @apply text-4xl opacity-40;
}

.hand-empty-text {
  @apply text-sm font-medium text-slate-400;
}

.hand-cards {
  @apply flex flex-wrap justify-center gap-3 px-4 py-3 rounded-2xl bg-slate-800/50 backdrop-blur-md border border-white/10 shadow-2xl;
  max-height: 200px;
  overflow-y: auto;
}

.hand-card {
  @apply relative w-28 h-40 rounded-xl cursor-pointer transition-all duration-300 select-none;

  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.hand-card:hover {
  @apply -translate-y-3 scale-105;
  box-shadow: 0 12px 24px rgba(139, 92, 246, 0.4);
  border-color: rgba(139, 92, 246, 0.6);
  background: rgba(30, 41, 59, 0.8);
}

.hand-card:active {
  @apply -translate-y-1 scale-98;
}

.hand-card-inner {
  @apply w-full h-full flex flex-col items-center p-3 rounded-xl;
}

.hand-card-media {
  @apply w-full h-20 flex items-center justify-center rounded-lg mb-2 overflow-hidden;
  background: rgba(15, 23, 42, 0.5);
}

.hand-card-image {
  @apply w-full h-full object-cover;
}

.hand-card-icon {
  @apply text-4xl filter drop-shadow-lg;
}

.hand-card-info {
  @apply flex flex-col items-center gap-1 w-full flex-1;
}

.hand-card-label {
  @apply text-xs font-semibold text-white/90 text-center line-clamp-2 w-full;
  word-break: break-word;
}

.hand-card-type {
  @apply text-[10px] font-medium text-slate-400 px-2 py-0.5 rounded-full bg-slate-700/50;
}

.hand-card-action {
  @apply absolute -bottom-2 left-1/2 -translate-x-1/2 px-2 py-1 rounded-full text-[10px] font-bold whitespace-nowrap opacity-0 transition-all duration-300;
  background: rgba(139, 92, 246, 0.9);
  color: white;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.5);
}

.hand-card:hover .hand-card-action {
  @apply opacity-100 -translate-y-2;
}

.action-text {
  @apply flex items-center gap-1;
}

.footer-text {
  @apply text-xs font-medium text-slate-300;
}

.hand-cards::-webkit-scrollbar {
  @apply w-1.5;
}

.hand-cards::-webkit-scrollbar-track {
  @apply rounded-full bg-slate-800/30;
}

.hand-cards::-webkit-scrollbar-thumb {
  @apply rounded-full bg-violet-600/50 hover:bg-violet-500/70;
}

@media (max-width: 640px) {
  .hand-container {
    @apply bottom-4 w-[95%];
  }

  .hand-cards {
    @apply gap-2 px-3 py-2;
  }

  .hand-card {
    @apply w-24 h-36;
  }

  .hand-card-icon {
    @apply text-3xl;
  }
}
</style>
