<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  x: { type: Number, required: true },
  y: { type: Number, required: true },
  username: { type: String, default: 'Player' },
  color: { type: String, default: '#8b5cf6' },
  zoom: { type: Number, default: 1 }
})

const markerStyle = computed(() => ({
  left: `${props.x}px`,
  top: `${props.y}px`,
  transform: `translate(-50%, -100%) scale(${props.zoom})`,
  borderColor: props.color
}))
</script>

<template>
  <div 
    class="absolute pointer-events-none z-50 transition-all duration-75"
    :style="markerStyle"
  >
    <svg 
      class="w-6 h-6 drop-shadow-lg" 
      viewBox="0 0 24 24" 
      fill="none" 
      :stroke="color"
      stroke-width="2"
    >
      <path d="M12 2L2 22L12 18L22 22L12 2Z" :fill="color + '30'" />
    </svg>
    
    <div 
      class="absolute top-full left-1/2 -translate-x-1/2 mt-1 px-2 py-1 rounded text-xs font-medium whitespace-nowrap"
      :style="{ 
        background: color + '20', 
        color: color,
        border: `1px solid ${color}50`
      }"
    >
      {{ username }}
    </div>
  </div>
</template>