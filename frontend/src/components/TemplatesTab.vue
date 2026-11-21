<script setup lang="ts">
import { ref } from 'vue'
import { LayoutGrid, Sparkles } from 'lucide-vue-next'
import type { CanvasFormat, CompositionPlan, ElementSize } from '../types'
import { requestManualComposition } from '../api/client'

const props = defineProps<{
  currentFormat: CanvasFormat
  currentSize: ElementSize
  currentPaletteId: string
}>()

const emit = defineEmits<{
  (e: 'composed', plan: CompositionPlan): void
}>()

const activeTemplateId = ref<string>('folder_wallet_coin')
const isLoading = ref(false)

interface TemplateItem {
  id: string
  title: string
  description: string
  keys: string[]
  isBackground: boolean
  badge: string
}

const mainTemplates: TemplateItem[] = [
  {
    id: 'phone_puzzle',
    title: 'Смартфон + Пазлы',
    description: 'Пазлы парят прямо над экраном телефона',
    keys: ['phone', 'puzzle'],
    isBackground: false,
    badge: 'Главные',
  },
  {
    id: 'book_phone',
    title: 'Книга + Смартфон',
    description: 'Телефон лежит на правой странице открытой книги',
    keys: ['book', 'phone'],
    isBackground: false,
    badge: 'Главные',
  },
  {
    id: 'folder_wallet_coin',
    title: 'Папка + Кошелёк + Монета',
    description: 'Папка сзади, кошелёк и монета впереди',
    keys: ['folder', 'wallet', 'coin'],
    isBackground: false,
    badge: 'Главные',
  },
]

const bgTemplates: TemplateItem[] = [
  {
    id: 'lamp_wallet_coin',
    title: 'Лампа (фон) + Кошелёк + Монета',
    description: 'Лампа в монохромном контуре, кошелёк и монета цветные',
    keys: ['lamp', 'wallet', 'coin'],
    isBackground: true,
    badge: 'С фоновыми',
  },
  {
    id: 'book_puzzle_pen',
    title: 'Книга (фон) + Пазлы + Ручка',
    description: 'Книга в монохромном контуре, пазлы и ручка цветные',
    keys: ['book', 'puzzle', 'pen'],
    isBackground: true,
    badge: 'С фоновыми',
  },
  {
    id: 'vase_headphones',
    title: 'Фоновый декор (ваза) + Наушники',
    description: 'Ваза с тюльпанами в моно-контуре на столе, наушники цветные',
    keys: ['vase', 'headphones'],
    isBackground: true,
    badge: 'С фоновыми',
  },
]

async function applyTemplate(tpl: TemplateItem) {
  if (isLoading.value) return
  isLoading.value = true
  activeTemplateId.value = tpl.id
  try {
    const plan = await requestManualComposition(
      tpl.keys,
      props.currentFormat,
      'assembled',
      props.currentSize,
      props.currentPaletteId,
      tpl.isBackground,
      tpl.id
    )
    emit('composed', plan)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="space-y-4 select-none">
    <div class="space-y-1">
      <div class="text-xs font-bold text-zinc-900 uppercase tracking-wider flex items-center gap-1.5">
        <LayoutGrid class="w-3.5 h-3.5 text-zinc-700" />
        <span>Канонические сцены Figma</span>
      </div>
      <p class="text-xs text-zinc-500 leading-normal">
        100% совпадение с примерами из раздела <strong class="text-zinc-800">Section 1</strong> макета ТЗ.
      </p>
    </div>

    <!-- Group 1: Main only -->
    <div class="space-y-2">
      <div class="text-[11px] font-bold text-zinc-600 uppercase tracking-wider flex items-center justify-between">
        <span>Пример только с Главными объектами</span>
      </div>

      <div class="space-y-1.5">
        <div
          v-for="tpl in mainTemplates"
          :key="tpl.id"
          @click="applyTemplate(tpl)"
          :class="[
            'p-2.5 rounded-md border text-left cursor-pointer transition-all flex flex-col gap-1',
            activeTemplateId === tpl.id
              ? 'border-zinc-950 bg-zinc-900 text-white shadow-sm'
              : 'border-zinc-200 bg-white hover:border-zinc-300 text-zinc-900'
          ]"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold">{{ tpl.title }}</span>
            <span
              :class="[
                'text-[10px] font-semibold px-1.5 py-0.5 rounded',
                activeTemplateId === tpl.id ? 'bg-zinc-800 text-zinc-300' : 'bg-zinc-100 text-zinc-600'
              ]"
            >
              {{ tpl.badge }}
            </span>
          </div>
          <p :class="['text-[11px] leading-tight', activeTemplateId === tpl.id ? 'text-zinc-400' : 'text-zinc-500']">
            {{ tpl.description }}
          </p>
        </div>
      </div>
    </div>

    <!-- Group 2: With background -->
    <div class="space-y-2 pt-1">
      <div class="text-[11px] font-bold text-zinc-600 uppercase tracking-wider flex items-center justify-between">
        <span>Пример с Фоновыми объектами</span>
      </div>

      <div class="space-y-1.5">
        <div
          v-for="tpl in bgTemplates"
          :key="tpl.id"
          @click="applyTemplate(tpl)"
          :class="[
            'p-2.5 rounded-md border text-left cursor-pointer transition-all flex flex-col gap-1',
            activeTemplateId === tpl.id
              ? 'border-zinc-950 bg-zinc-900 text-white shadow-sm'
              : 'border-zinc-200 bg-white hover:border-zinc-300 text-zinc-900'
          ]"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold">{{ tpl.title }}</span>
            <span
              :class="[
                'text-[10px] font-semibold px-1.5 py-0.5 rounded',
                activeTemplateId === tpl.id ? 'bg-zinc-800 text-zinc-300' : 'bg-purple-100 text-purple-700'
              ]"
            >
              {{ tpl.badge }}
            </span>
          </div>
          <p :class="['text-[11px] leading-tight', activeTemplateId === tpl.id ? 'text-zinc-400' : 'text-zinc-500']">
            {{ tpl.description }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
