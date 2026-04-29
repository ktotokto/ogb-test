<script setup>
import { ref } from 'vue'
import { Gamepad2, Save } from 'lucide-vue-next'

const templateName = ref('')
const description = ref('')

const saveTemplate = () => {
  console.log('Сохранение шаблона:', templateName.value, description.value)
}
</script>

<template>
  <div class="space-y-4">
    <div class="text-center py-8">
      <Gamepad2 class="w-16 h-16 mx-auto mb-4 text-violet-400 opacity-50" />
      <h3 class="text-lg font-semibold text-white mb-2">Шаблоны игры</h3>
      <p class="text-sm text-slate-400 mb-4">Сохраните текущую расстановку как шаблон</p>
    </div>

    <input
      v-model="templateName"
      type="text"
      placeholder="Название шаблона"
      class="w-full px-4 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white placeholder-slate-400 focus:outline-none focus:border-violet-500"
    />

    <textarea
      v-model="description"
      placeholder="Описание (необязательно)"
      rows="3"
      class="w-full px-4 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white placeholder-slate-400 focus:outline-none focus:border-violet-500 resize-none"
    />

    <button
      @click="saveTemplate"
      class="w-full px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg transition-all flex items-center justify-center gap-2"
    >
      <Save class="w-4 h-4" />
      Сохранить шаблон
    </button>
  </div>
</template>