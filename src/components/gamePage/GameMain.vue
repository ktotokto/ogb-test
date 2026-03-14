<script setup>
import GameBoard from './gameMain/GameBoard.vue';
import GameTools from './gameMain/GameTools.vue';
import PlayersList from './gameMain/PlayersList.vue';



</script>


<template>

    <section class="flex">
        <PlayersList />
        <GameTools />
        <GameBoard />
    </section>
    
</template>
