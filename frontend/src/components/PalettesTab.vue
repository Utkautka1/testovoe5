<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Palette as PaletteIcon, Check } from 'lucide-vue-next'
import type { Palette } from '../types'
import { fetchPalettes } from '../api/client'

const props = defineProps<{
  activePaletteId: string
}>()

const emit = defineEmits<{
  (e: 'select', palette: Palette): void
}>()

const palettes = ref<Palette[]>([])

async function loadPalettes() {
  try {
    palettes.value = await fetchPalettes()
  } catch (e) {
    console.error(e)
  }
}

function selectPalette(p: Palette) {
  emit('select', p)
}

onMounted(loadPalettes)
</script>

<template>
  <div class="space-y-3.5 select-none">
    <div class="space-y-1">
      <div class="text-xs font-bold text-zinc-900 uppercase tracking-wider flex items-center gap-1.5">
        <PaletteIcon class="w-3.5 h-3.5 text-zinc-700" />
        <span>Цветовые переменные (Tokens)</span>
      </div>
      <p class="text-xs text-zinc-500">
        Автоматическая перекраска векторных путей композиции по правилам дизайн-системы.
      </p>
    </div>

    <div class="space-y-2">
      <div
        v-for="p in palettes"
        :key="p.id"
        @click="selectPalette(p)"
        :class="[
          'p-3 rounded-md border transition-all cursor-pointer flex flex-col gap-2',
          activePaletteId === p.id
            ? 'border-zinc-900 bg-zinc-50 ring-1 ring-zinc-900 shadow-sm'
            : 'border-zinc-200 bg-white hover:border-zinc-300'
        ]"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-zinc-900">{{ p.name }}</span>
          <div
            v-if="activePaletteId === p.id"
            class="w-3.5 h-3.5 rounded-full bg-zinc-900 text-white flex items-center justify-center text-[9px]"
          >
            <Check class="w-2.5 h-2.5 stroke-[3]" />
          </div>
        </div>

        <!-- Design Token Swatches -->
        <div class="flex items-center gap-1.5">
          <!-- Background swatch -->
          <div
            class="w-6 h-6 rounded border border-zinc-300 flex items-center justify-center text-[9px] font-bold text-zinc-600"
            :style="{ backgroundColor: p.background }"
            title="Фон"
          >
            Bg
          </div>

          <!-- Color roles -->
          <div class="flex items-center gap-1 flex-1">
            <div
              class="h-6 flex-1 rounded border border-black/5"
              :style="{ backgroundColor: p.accent_primary }"
              title="Основной акцент"
            ></div>
            <div
              class="h-6 flex-1 rounded border border-black/5"
              :style="{ backgroundColor: p.accent_secondary }"
              title="Вторичный акцент"
            ></div>
            <div
              class="h-6 flex-1 rounded border border-black/5"
              :style="{ backgroundColor: p.accent_light }"
              title="Светлый тон"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
