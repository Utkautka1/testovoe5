<script setup lang="ts">
import { ref } from 'vue'
import { SlidersHorizontal, Loader2, Info } from 'lucide-vue-next'
import type { CanvasFormat, CompositionPlan, ElementSize } from '../types'
import { requestAIComposition } from '../api/client'

const props = defineProps<{
  currentFormat: CanvasFormat
  currentSize: ElementSize
}>()

const emit = defineEmits<{
  (e: 'composed', plan: CompositionPlan): void
}>()

const promptText = ref('Современный мобильный банкинг и сбережения')
const withBackground = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const lastExplanation = ref('')

const suggestions = [
  'Финтех и мобильный банкинг',
  'Образование и база знаний',
  'Командный стартап и разработка',
  'Медиатека и подкасты',
]

function useSuggestion(s: string) {
  promptText.value = s
  handleGenerate()
}

function setWithBackground(val: boolean) {
  if (withBackground.value === val) return
  withBackground.value = val
  handleGenerate()
}

async function handleGenerate() {
  if (!promptText.value.trim() || isLoading.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    const plan = await requestAIComposition(
      promptText.value,
      props.currentFormat,
      props.currentSize,
      withBackground.value
    )
    lastExplanation.value = plan.explanation || ''
    emit('composed', plan)
  } catch (err: any) {
    errorMessage.value = err.message || 'Ошибка генерации'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="space-y-1">
      <div class="text-xs font-bold text-zinc-900 uppercase tracking-wider flex items-center gap-1.5">
        <SlidersHorizontal class="w-3.5 h-3.5 text-zinc-700" />
        <span>Генерация по брифу</span>
      </div>
      <p class="text-xs text-zinc-500 leading-normal">
        Интеллектуальный подбор объектов из библиотеки 20 иллюстраций и расчёт композиционной сетки.
      </p>
    </div>

    <!-- Brief input -->
    <div class="space-y-2">
      <textarea
        v-model="promptText"
        rows="3"
        placeholder="Тема, метафора или заголовок материала..."
        class="w-full text-xs font-medium text-zinc-900 bg-zinc-50 border border-zinc-200 rounded-md p-2.5 focus:outline-none focus:ring-1 focus:ring-zinc-800 focus:bg-white resize-none"
      ></textarea>

      <!-- Preset brief chips -->
      <div class="flex flex-wrap gap-1">
        <button
          v-for="s in suggestions"
          :key="s"
          type="button"
          @click="useSuggestion(s)"
          class="text-[11px] font-medium bg-zinc-100 hover:bg-zinc-200 text-zinc-700 px-2 py-0.5 rounded border border-zinc-200 transition"
        >
          {{ s }}
        </button>
      </div>
    </div>

    <!-- Composition Mode: Only Main vs With Background -->
    <div class="space-y-1.5">
      <div class="text-[11px] font-semibold text-zinc-700 flex items-center justify-between">
        <span>Тип композиции (Figma Section 1)</span>
      </div>
      <div class="grid grid-cols-2 gap-1 bg-zinc-100 p-0.5 rounded-md border border-zinc-200 text-xs font-semibold">
        <button
          type="button"
          @click="setWithBackground(false)"
          :class="[
            'py-1.5 px-2 rounded transition-colors text-center text-[11px]',
            !withBackground ? 'bg-white text-zinc-900 shadow-sm' : 'text-zinc-500 hover:text-zinc-900'
          ]"
        >
          Только главные
        </button>
        <button
          type="button"
          @click="setWithBackground(true)"
          :class="[
            'py-1.5 px-2 rounded transition-colors text-center text-[11px]',
            withBackground ? 'bg-white text-zinc-900 shadow-sm' : 'text-zinc-500 hover:text-zinc-900'
          ]"
        >
          С фоновыми (mono)
        </button>
      </div>
    </div>

    <!-- Action button -->
    <button
      @click="handleGenerate"
      :disabled="isLoading || !promptText.trim()"
      class="w-full py-2 px-3 bg-zinc-900 hover:bg-zinc-800 disabled:opacity-50 text-white font-semibold text-xs rounded-md shadow-sm transition flex items-center justify-center gap-2 active:scale-98"
    >
      <Loader2 v-if="isLoading" class="w-3.5 h-3.5 animate-spin" />
      <span v-else>Сгенерировать композицию</span>
    </button>

    <div v-if="errorMessage" class="p-2.5 bg-red-50 text-red-700 text-xs rounded-md border border-red-200">
      {{ errorMessage }}
    </div>

    <!-- Studio Rationale Summary -->
    <div v-if="lastExplanation" class="p-3 bg-zinc-50 border border-zinc-200 rounded-md space-y-1">
      <div class="flex items-center gap-1.5 text-[11px] font-semibold text-zinc-700">
        <Info class="w-3 h-3 text-zinc-500" />
        <span>Семантическое соответствие:</span>
      </div>
      <p class="text-[11px] text-zinc-600 leading-relaxed">
        {{ lastExplanation }}
      </p>
    </div>
  </div>
</template>
