<script setup>
import GameBoard from './gameMain/GameBoard.vue'
import GameTools from './gameMain/GameTools.vue'
import PlayersList from './gameMain/PlayersList.vue'

</script>

<template>
    <div class="h-screen w-full bg-slate-950 text-white flex flex-col overflow-hidden">

        <div class="flex-1 flex overflow-hidden">

            <aside class="w-3/12 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
                <PlayersList class="flex-1 overflow-y-auto no-scrollbar" />
                <GameTools class="shrink-0" />
            </aside>

            <main class="flex-1 relative overflow-hidden">
                <GameBoard class="absolute inset-0 h-full w-9/12" />
            </main>
        </div>
    </div>
</template>