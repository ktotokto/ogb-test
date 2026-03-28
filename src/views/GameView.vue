<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import GamePage from '@/components/gamePage/gamePage.vue'

const route = useRoute()
const sessionId = route.params.sessionId
</script>

<template>
  <GamePage :session-id="sessionId" />
</template>