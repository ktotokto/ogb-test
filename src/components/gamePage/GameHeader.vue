<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const time = ref(0)
let flag = true
let intervalId = null

onMounted(() => {
    intervalId = setInterval(() => {
        time.value++;
        if (time.value > 30) {
            flag = !flag
        }
    }, 1000);
})


onUnmounted(() => {
    if (intervalId) { clearInterval(intervalId) }
})

</script>


<template>
    <nav class="w-10/12 mx-auto flex justify-between flex-wrap;">
        <div class="session w-full md:w-1/2 lg:w-3/12">
            <h2>5F3-8DF-1XD</h2>
        </div>
        <div class="flex justify-center items-center"> 
            <div class="flex gap-2 p-4 bg-white/50 backdrop-blur-sm rounded-2xl shadow-inner border border-gray-100">
                <div class="bg-white p-3 rounded-xl shadow w-16 text-center">
                    <div class="text-3xl font-bold text-blue-600">{{ time }}</div>
                    <div class="text-xs uppercase text-gray-500">Часов</div>
                </div>
                <div class="bg-white p-3 rounded-xl shadow w-16 text-center">
                    <div class="text-3xl font-bold text-blue-600">{{ time }}</div>
                    <div class="text-xs uppercase text-gray-500">Мин</div>
                </div>
                <div class="bg-white p-3 rounded-xl shadow w-16 text-center">
                    <div class="text-3xl font-bold text-blue-600">{{ time }}</div>
                    <div class="text-xs uppercase text-gray-500">Сек</div>
                </div>
            </div>
        </div>
        <div class=" max-h-[50%]menu-bar flex w-full md:w-1/2 lg:w-3/12 ">
            <a href="#" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Save</a>
            <a href="#" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Invite</a>
            <a href="#" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Leave</a>
        </div>
    </nav>
</template>
