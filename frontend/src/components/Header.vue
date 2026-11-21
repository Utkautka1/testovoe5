<script setup lang="ts">
import { Download, Trash2, Copy, ArrowUp, ArrowDown, Shapes } from 'lucide-vue-next'
import type { CanvasFormat } from '../types'
import { fabricService } from '../services/fabricService'

const props = defineProps<{
  currentFormat: CanvasFormat
}>()

const emit = defineEmits<{
  (e: 'update:format', fmt: CanvasFormat): void
}>()

function onFormatChange(e: Event) {
  const target = e.target as HTMLSelectElement
  emit('update:format', target.value as CanvasFormat)
}

function exportSvg() {
  const dateStr = new Date().toISOString().slice(0, 10)
  fabricService.downloadSVG(`composition-${props.currentFormat}-${dateStr}.svg`)
}
</script>

<template>
  <header class="h-14 border-b border-zinc-200 bg-white px-5 flex items-center justify-between z-20 select-none">
    <!-- Brand -->
    <div class="flex items-center gap-2.5">
      <div class="w-7 h-7 rounded bg-zinc-900 flex items-center justify-center text-white shadow-xs">
        <Shapes class="w-4 h-4 stroke-[2.2]" />
      </div>
      <div class="flex items-baseline gap-2">
        <span class="text-sm font-bold tracking-tight text-zinc-950">Studio Vector</span>
        <span class="text-[11px] font-medium text-zinc-400">v1.0</span>
      </div>
    </div>

    <!-- Center toolbar: Format Picker -->
    <div class="flex items-center">
      <div class="flex items-center bg-zinc-100 p-0.5 rounded-md border border-zinc-200 text-xs">
        <span class="px-2.5 text-zinc-400 font-medium text-[11px]">Формат холста:</span>
        <select
          :value="currentFormat"
          @change="onFormatChange"
          class="bg-white text-xs font-semibold text-zinc-800 rounded px-2.5 py-1 border-0 shadow-sm focus:outline-none cursor-pointer"
        >
          <option value="1200x630">1200 × 630 • Горизонтальный</option>
          <option value="1000x1000">1000 × 1000 • Квадрат</option>
          <option value="800x1200">800 × 1200 • Вертикальный</option>
        </select>
      </div>
    </div>

    <!-- Right Actions -->
    <div class="flex items-center gap-2">
      <div class="flex items-center bg-zinc-100 p-0.5 rounded-md border border-zinc-200">
        <button
          @click="fabricService.bringForward()"
          title="Слой выше"
          class="p-1.5 text-zinc-600 hover:text-zinc-900 hover:bg-white rounded transition"
        >
          <ArrowUp class="w-3.5 h-3.5" />
        </button>
        <button
          @click="fabricService.sendBackward()"
          title="Слой ниже"
          class="p-1.5 text-zinc-600 hover:text-zinc-900 hover:bg-white rounded transition"
        >
          <ArrowDown class="w-3.5 h-3.5" />
        </button>
        <button
          @click="fabricService.duplicateSelected()"
          title="Дублировать"
          class="p-1.5 text-zinc-600 hover:text-zinc-900 hover:bg-white rounded transition"
        >
          <Copy class="w-3.5 h-3.5" />
        </button>
        <button
          @click="fabricService.deleteSelected()"
          title="Удалить"
          class="p-1.5 text-zinc-600 hover:text-red-600 hover:bg-white rounded transition"
        >
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>

      <button
        @click="exportSvg"
        class="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-zinc-900 hover:bg-black text-white text-xs font-semibold rounded-md shadow-sm transition active:scale-95"
      >
        <Download class="w-3.5 h-3.5" />
        <span>Экспорт SVG</span>
      </button>
    </div>
  </header>
</template>
