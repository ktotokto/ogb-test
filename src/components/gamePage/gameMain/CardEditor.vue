<script setup lang="ts">
import { ref, watch } from 'vue'
import { X, Upload, Image, RotateCcw } from 'lucide-vue-next'

const props = defineProps({
  card: { type: Object, required: true }
})

const emit = defineEmits(['save', 'close'])

const editedCard = ref({ ...props.card })

watch(() => props.card, (newCard) => {
  editedCard.value = { ...newCard }
}, { deep: true })

const handleImageUpload = (field, event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    editedCard.value[field] = e.target.result
  }
  reader.readAsDataURL(file)
}

const removeImage = (field) => {
  editedCard.value[field] = null
}

const handleSave = () => {
  emit('save', { ...editedCard.value })
}

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[200] flex items-center justify-center" @click="handleClose">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      <div class="relative w-[520px] bg-slate-900 rounded-2xl border border-white/10 shadow-2xl overflow-hidden"
        @click.stop>
        <div class="flex items-center justify-between p-5 border-b border-white/10">
          <h2 class="text-lg font-bold text-white">Редактор карты</h2>
          <button @click="handleClose" class="text-slate-400 hover:text-white transition-colors">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="p-5 space-y-5 max-h-[70vh] overflow-y-auto">
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Название карты</label>
            <input v-model="editedCard.name" type="text"
              class="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all"
              placeholder="Введите название..." />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Лицевая сторона</label>
              <div
                class="relative w-full aspect-[2/3] rounded-xl border-2 border-dashed border-white/10 overflow-hidden bg-slate-800/50 group hover:border-violet-500/50 transition-colors">
                <template v-if="editedCard.frontImage">
                  <img :src="editedCard.frontImage" class="w-full h-full object-cover" />
                  <div
                    class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <button @click="removeImage('frontImage')"
                      class="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                      title="Удалить изображение">
                      <X class="w-4 h-4" />
                    </button>
                  </div>
                </template>
                <template v-else>
                  <label
                    class="absolute inset-0 flex flex-col items-center justify-center cursor-pointer text-slate-500 hover:text-violet-400 transition-colors">
                    <Upload class="w-8 h-8 mb-2" />
                    <span class="text-xs">Загрузить</span>
                    <input type="file" accept="image/*" class="hidden"
                      @change="handleImageUpload('frontImage', $event)" />
                  </label>
                </template>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Оборотная сторона</label>
              <div
                class="relative w-full aspect-[2/3] rounded-xl border-2 border-dashed border-white/10 overflow-hidden bg-slate-800/50 group hover:border-violet-500/50 transition-colors">
                <template v-if="editedCard.backImage">
                  <img :src="editedCard.backImage" class="w-full h-full object-cover" />
                  <div
                    class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <button @click="removeImage('backImage')"
                      class="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                      title="Удалить изображение">
                      <X class="w-4 h-4" />
                    </button>
                  </div>
                </template>
                <template v-else>
                  <label
                    class="absolute inset-0 flex flex-col items-center justify-center cursor-pointer text-slate-500 hover:text-violet-400 transition-colors">
                    <Upload class="w-8 h-8 mb-2" />
                    <span class="text-xs">Загрузить</span>
                    <input type="file" accept="image/*" class="hidden"
                      @change="handleImageUpload('backImage', $event)" />
                  </label>
                </template>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Предпросмотр</label>
            <div class="flex gap-4 justify-center">
              <div class="text-center">
                <div
                  class="w-20 h-28 rounded-lg border border-white/10 overflow-hidden bg-slate-800 flex items-center justify-center">
                  <img v-if="editedCard.frontImage" :src="editedCard.frontImage" class="w-full h-full object-cover" />
                  <span v-else class="text-xs text-slate-500">Лицо</span>
                </div>
                <span class="text-xs text-slate-400 mt-1 block">Лицо</span>
              </div>
              <div class="text-center">
                <div
                  class="w-20 h-28 rounded-lg border border-white/10 overflow-hidden bg-slate-800 flex items-center justify-center">
                  <img v-if="editedCard.backImage" :src="editedCard.backImage" class="w-full h-full object-cover" />
                  <div v-else
                    class="w-full h-full bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center">
                    <span class="text-2xl">🎴</span>
                  </div>
                </div>
                <span class="text-xs text-slate-400 mt-1 block">Рубашка</span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex gap-3 p-5 border-t border-white/10 bg-slate-800/50">
          <button @click="handleClose"
            class="flex-1 py-2.5 px-4 rounded-xl bg-slate-700 hover:bg-slate-600 text-slate-300 font-medium transition-colors">
            Отмена
          </button>
          <button @click="handleSave"
            class="flex-1 py-2.5 px-4 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium transition-colors shadow-lg shadow-violet-500/20">
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
input[type="file"] {
  display: none;
}
</style>
