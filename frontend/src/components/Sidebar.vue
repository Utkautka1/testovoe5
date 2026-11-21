<script setup lang="ts">
import { ref } from 'vue'
import { SlidersHorizontal, FolderKanban, Palette as PaletteIcon, LayoutGrid } from 'lucide-vue-next'
import type { CanvasFormat, CompositionPlan, ElementSize, Palette } from '../types'
import AIComposerTab from './AIComposerTab.vue'
import CatalogTab from './CatalogTab.vue'
import PalettesTab from './PalettesTab.vue'
import TemplatesTab from './TemplatesTab.vue'

defineProps<{
  currentFormat: CanvasFormat
  currentSize: ElementSize
  activePaletteId: string
}>()

const emit = defineEmits<{
  (e: 'composed', plan: CompositionPlan): void
  (e: 'select-palette', palette: Palette): void
}>()

const activeTab = ref<'templates' | 'ai' | 'catalog' | 'palettes'>('templates')

function setTab(tab: 'templates' | 'ai' | 'catalog' | 'palettes') {
  activeTab.value = tab
}
</script>

<template>
  <aside class="w-80 border-r border-zinc-200 bg-white flex flex-col h-[calc(100vh-3.5rem)] z-10 select-none">
    <!-- Segmented Tab Navigation -->
    <div class="flex border-b border-zinc-200 bg-zinc-50 p-1 gap-1 overflow-x-auto">
      <button
        @click="setTab('templates')"
        :class="[
          'flex-1 py-1 px-1.5 text-[11px] font-semibold rounded transition flex items-center justify-center gap-1 min-w-[64px]',
          activeTab === 'templates' ? 'bg-white text-zinc-950 shadow-sm border border-zinc-200' : 'text-zinc-500 hover:text-zinc-900'
        ]"
      >
        <LayoutGrid class="w-3 h-3" />
        <span>Сцены ТЗ</span>
      </button>

      <button
        @click="setTab('ai')"
        :class="[
          'flex-1 py-1 px-1.5 text-[11px] font-semibold rounded transition flex items-center justify-center gap-1 min-w-[56px]',
          activeTab === 'ai' ? 'bg-white text-zinc-950 shadow-sm border border-zinc-200' : 'text-zinc-500 hover:text-zinc-900'
        ]"
      >
        <SlidersHorizontal class="w-3 h-3" />
        <span>Бриф</span>
      </button>

      <button
        @click="setTab('catalog')"
        :class="[
          'flex-1 py-1 px-1.5 text-[11px] font-semibold rounded transition flex items-center justify-center gap-1 min-w-[56px]',
          activeTab === 'catalog' ? 'bg-white text-zinc-950 shadow-sm border border-zinc-200' : 'text-zinc-500 hover:text-zinc-900'
        ]"
      >
        <FolderKanban class="w-3 h-3" />
        <span>Ассеты</span>
      </button>

      <button
        @click="setTab('palettes')"
        :class="[
          'flex-1 py-1 px-1.5 text-[11px] font-semibold rounded transition flex items-center justify-center gap-1 min-w-[56px]',
          activeTab === 'palettes' ? 'bg-white text-zinc-950 shadow-sm border border-zinc-200' : 'text-zinc-500 hover:text-zinc-900'
        ]"
      >
        <PaletteIcon class="w-3 h-3" />
        <span>Палитры</span>
      </button>
    </div>

    <!-- Tab Contents -->
    <div class="flex-1 overflow-y-auto p-4">
      <TemplatesTab
        v-if="activeTab === 'templates'"
        :current-format="currentFormat"
        :current-size="currentSize"
        :current-palette-id="activePaletteId"
        @composed="emit('composed', $event)"
      />

      <AIComposerTab
        v-else-if="activeTab === 'ai'"
        :current-format="currentFormat"
        :current-size="currentSize"
        @composed="emit('composed', $event)"
      />

      <CatalogTab
        v-else-if="activeTab === 'catalog'"
        :current-format="currentFormat"
        :current-size="currentSize"
        :current-palette-id="activePaletteId"
        @composed="emit('composed', $event)"
      />

      <PalettesTab
        v-else-if="activeTab === 'palettes'"
        :active-palette-id="activePaletteId"
        @select="emit('select-palette', $event)"
      />
    </div>
  </aside>
</template>
