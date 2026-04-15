<script setup>
const props = defineProps({
  cards: Array
});
</script>

<template>
  <div class="hand">
    <div v-for="card in cards" :key="card.id">
      {{ card.name }}
    </div>
  </div>
</template>