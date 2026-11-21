<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-vue-next'
import type { CanvasFormat, Palette } from '../types'
import { fabricService } from '../services/fabricService'

const props = defineProps<{
  currentFormat: CanvasFormat
  activePalette: Palette
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const zoomLevel = ref(0.7)

function getFormatDimensions(fmt: CanvasFormat): [number, number] {
  if (fmt === '1000x1000') return [1000, 1000]
  if (fmt === '800x1200') return [800, 1200]
  return [1200, 630]
}

function initCanvas() {
  if (!canvasRef.value) return
  const [w, h] = getFormatDimensions(props.currentFormat)
  fabricService.init(canvasRef.value, w, h, props.activePalette.background)
}

function updateCanvasSize() {
  const [w, h] = getFormatDimensions(props.currentFormat)
  fabricService.setDimensions(w, h)
}

function adjustZoom(delta: number) {
  zoomLevel.value = Math.min(Math.max(zoomLevel.value + delta, 0.3), 1.5)
}

function fitToScreen() {
  zoomLevel.value = 0.65
}

watch(() => props.currentFormat, updateCanvasSize)

onMounted(() => {
  initCanvas()
  fitToScreen()
})
</script>

<template>
  <main class="flex-1 bg-[#EBEBEB] overflow-hidden flex flex-col relative select-none">
    <!-- Top status bar -->
    <div class="h-9 bg-white/90 backdrop-blur-sm border-b border-zinc-200 px-4 flex items-center justify-between text-xs text-zinc-500 z-10">
      <div class="flex items-center gap-2">
        <span class="font-semibold text-zinc-800 tracking-tight">{{ currentFormat }} PX</span>
        <span class="text-zinc-300">•</span>
        <span class="text-[11px] text-zinc-500">Векторный артборд</span>
      </div>

      <!-- Zoom controller -->
      <div class="flex items-center gap-1 bg-zinc-100 rounded p-0.5 border border-zinc-200">
        <button
          @click="adjustZoom(-0.1)"
          title="Отдалить"
          class="p-1 hover:bg-white rounded text-zinc-600 transition"
        >
          <ZoomOut class="w-3 h-3" />
        </button>
        <span class="px-1.5 text-[10px] font-bold text-zinc-700 min-w-[36px] text-center">
          {{ Math.round(zoomLevel * 100) }}%
        </span>
        <button
          @click="adjustZoom(0.1)"
          title="Приблизить"
          class="p-1 hover:bg-white rounded text-zinc-600 transition"
        >
          <ZoomIn class="w-3 h-3" />
        </button>
        <button
          @click="fitToScreen"
          title="По размеру"
          class="p-1 hover:bg-white rounded text-zinc-600 transition"
        >
          <Maximize2 class="w-3 h-3" />
        </button>
      </div>
    </div>

    <!-- Centered Canvas with Figma-like neutral backdrop -->
    <div class="flex-1 overflow-auto flex items-center justify-center p-10">
      <div
        class="transition-transform duration-100 origin-center shadow-2xl rounded-sm overflow-hidden border border-zinc-300 flex-shrink-0"
        :style="{ transform: `scale(${zoomLevel})` }"
      >
        <canvas ref="canvasRef"></canvas>
      </div>
    </div>
  </main>
</template>
