<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { CanvasFormat, CompositionPlan, ElementSize, Palette } from './types'
import { fetchPalettes, requestManualComposition } from './api/client'
import { fabricService } from './services/fabricService'
import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'
import CanvasArea from './components/CanvasArea.vue'

const currentFormat = ref<CanvasFormat>('1200x630')
const currentSize = ref<ElementSize>('L')
const palettes = ref<Palette[]>([])

const activePalette = ref<Palette>({
  id: 'warm_sun',
  name: 'Тёплая солнечная',
  background: '#FFFDF5',
  accent_primary: '#D27532',
  accent_secondary: '#F9ECB0',
  accent_light: '#FDD7B9',
  neutral_dark: '#181817',
})

const lastArchetypeId = ref<string>('folder_wallet_coin')
const lastElementKeys = ref<string[]>(['folder', 'wallet', 'coin'])
const lastIncludeBg = ref<boolean>(false)

async function onCompositionCreated(plan: CompositionPlan) {
  currentFormat.value = plan.format
  currentSize.value = plan.size
  const targetPal = palettes.value.find(p => p.id === plan.palette_id) || activePalette.value
  activePalette.value = targetPal
  await fabricService.renderComposition(plan.elements, plan.size, targetPal, plan.background_lines)
}

function onPaletteSelect(pal: Palette) {
  activePalette.value = pal
  fabricService.applyPalette(pal)
}

async function onFormatUpdate(fmt: CanvasFormat) {
  currentFormat.value = fmt
  try {
    const updatedPlan = await requestManualComposition(
      lastElementKeys.value,
      fmt,
      'assembled',
      currentSize.value,
      activePalette.value.id,
      lastIncludeBg.value,
      lastArchetypeId.value
    )
    await onCompositionCreated(updatedPlan)
  } catch (e) {
    console.error('Format update error:', e)
  }
}

function onSizeUpdate(size: ElementSize) {
  currentSize.value = size
}

async function initDefaultComposition() {
  try {
    palettes.value = await fetchPalettes()
    const violet = palettes.value.find(p => p.id === 'violet_dusk') || palettes.value[0]
    if (violet) {
      activePalette.value = violet
    }
    const defaultPlan = await requestManualComposition(
      lastElementKeys.value,
      currentFormat.value,
      'assembled',
      currentSize.value,
      activePalette.value.id,
      lastIncludeBg.value,
      lastArchetypeId.value
    )
    await onCompositionCreated(defaultPlan)
  } catch (e) {
    console.error('Init error:', e)
  }
}

onMounted(initDefaultComposition)
</script>

<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-slate-100 font-sans">
    <Header
      :current-format="currentFormat"
      @update:format="onFormatUpdate"
    />

    <div class="flex-1 flex overflow-hidden">
      <Sidebar
        :current-format="currentFormat"
        :current-size="currentSize"
        :active-palette-id="activePalette.id"
        @composed="onCompositionCreated"
        @select-palette="onPaletteSelect"
      />

      <CanvasArea
        :current-format="currentFormat"
        :active-palette="activePalette"
      />
    </div>
  </div>
</template>
