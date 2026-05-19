<script setup>
import { ref, computed } from 'vue'
import { Layers, Square, Gamepad2, Trees } from 'lucide-vue-next'
import DeckEditor from './editor/DeckEditor.vue'
import ObjectEditor from './editor/ObjectEditor.vue'
import TemplateEditor from './editor/TemplateEditor.vue'
import EnvironmentEditor from './editor/EnvironmentEditor.vue'

const isOpen = ref(false)
const activeTab = ref('decks')

const tabs = [
  { id: 'decks', label: 'Колоды', icon: Layers },
  { id: 'objects', label: 'Объекты', icon: Square },
  { id: 'templates', label: 'Шаблоны игры', icon: Gamepad2 },
  { id: 'environment', label: 'Окружение', icon: Trees }
]

const toggleEditor = () => {
  isOpen.value = !isOpen.value
}

const setActiveTab = (tabId) => {
  activeTab.value = tabId
}

const activeComponent = computed(() => {
  const components = {
    decks: DeckEditor,
    objects: ObjectEditor,
    templates: TemplateEditor,
    environment: EnvironmentEditor
  }
  return components[activeTab.value] || DeckEditor
})
</script>

<template>
  <button
    @click="toggleEditor"
    :class="[
      'fixed top-4 right-6 z-50 px-4 py-2 rounded-xl font-medium transition-all flex items-center gap-2 shadow-lg',
      isOpen
        ? 'bg-violet-600 hover:bg-violet-500 text-white'
        : 'bg-slate-800/80 hover:bg-slate-700 text-white border border-white/10'
    ]"
  >
    <Layers class="w-4 h-4" />
    {{ isOpen ? 'Закрыть' : 'Редактор' }}
  </button>

  <aside
    :class="[
      'fixed top-0 right-0 h-full left-0 bg-slate-900/95 backdrop-blur-md border-l border-white/10 flex transition-all duration-300 z-40',
      isOpen ? 'w-95 translate-x-0' : 'w-96 translate-x-full'
    ]"
  >
    <div class="flex-1 flex flex-col overflow-hidden">
      <div class="p-4 border-b border-white/10">
        <h2 class="text-lg font-semibold text-white flex items-center gap-2">
          <span class="w-1 h-6 bg-violet-500 rounded-full"></span>
          Редактор
        </h2>
      </div>

      <div class="grid grid-cols-2 gap-3 p-4 border-b border-white/10">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="setActiveTab(tab.id)"
          :class="[
            'px-4 py-3 rounded-xl font-medium transition-all flex flex-col items-center gap-2 text-sm',
            activeTab === tab.id
              ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/30'
              : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700 hover:text-white border border-white/5'
          ]"
        >
          <component :is="tab.icon" class="w-5 h-5" />
          {{ tab.label }}
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-4">
        <component :is="activeComponent" @close="isOpen = false" />
      </div>
    </div>
  </aside>
</template>