<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Plus, Check, FolderKanban } from 'lucide-vue-next'
import type { CanvasFormat, CompositionPlan, ElementSize, LayoutPreset, LibraryItem } from '../types'
import { fetchLibrary, requestManualComposition } from '../api/client'
import { fabricService } from '../services/fabricService'

const props = defineProps<{
  currentFormat: CanvasFormat
  currentSize: ElementSize
  currentPaletteId: string
}>()

const emit = defineEmits<{
  (e: 'composed', plan: CompositionPlan): void
}>()

const items = ref<LibraryItem[]>([])
const searchQuery = ref('')
const selectedCategory = ref('all')
const selectedKeys = ref<string[]>([])
const selectedPreset = ref<LayoutPreset>('assembled')
const withBackground = ref(false)
const isLoading = ref(false)

const categories = [
  { id: 'all', label: 'Все' },
  { id: 'study', label: 'Учёба' },
  { id: 'finance', label: 'Финансы' },
  { id: 'work', label: 'Работа' },
  { id: 'tech', label: 'IT' },
  { id: 'media', label: 'Медиа' },
]

async function loadItems() {
  try {
    items.value = await fetchLibrary(searchQuery.value, props.currentSize)
  } catch (e) {
    console.error(e)
  }
}

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (item.size !== props.currentSize) return false
    if (selectedCategory.value !== 'all' && item.category !== selectedCategory.value) return false
    return true
  })
})

function toggleSelect(key: string) {
  const idx = selectedKeys.value.indexOf(key)
  if (idx > -1) {
    selectedKeys.value.splice(idx, 1)
  } else {
    selectedKeys.value.push(key)
  }
}

const OBJECT_BASE_SCALES: Record<string, number> = {
  book: 0.35,
  folder: 0.36,
  lamp: 0.26,
  headphones: 0.38,
  phone: 0.38,
  wallet: 0.44,
  puzzle: 0.34,
  pen: 0.42,
  coin: 0.44,
}

function getObjectScale(key: string, size: ElementSize): number {
  const base = OBJECT_BASE_SCALES[key] || 0.38
  return size === 'S' ? base * 0.85 : base
}

async function addSingleToCanvas(item: LibraryItem) {
  const canvas = fabricService.getCanvas()
  const cx = canvas ? canvas.getWidth() / 2 : 400
  const cy = canvas ? canvas.getHeight() / 2 : 300
  const scale = getObjectScale(item.key, props.currentSize)
  await fabricService.loadElement({
    element_id: `${item.key}_${Date.now()}`,
    key: item.key,
    x: cx,
    y: cy,
    scale_x: scale,
    scale_y: scale,
    rotation: 0,
    z_index: 2,
    is_background: item.type === 'background',
    svg_path: item.svg_path,
    width: item.width,
    height: item.height,
  }, props.currentSize)
}

async function handleComposeSelected() {
  if (selectedKeys.value.length === 0 || isLoading.value) return
  isLoading.value = true
  try {
    const plan = await requestManualComposition(
      selectedKeys.value,
      props.currentFormat,
      selectedPreset.value,
      props.currentSize,
      props.currentPaletteId,
      withBackground.value
    )
    emit('composed', plan)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadItems)
</script>

<template>
  <div class="space-y-3.5 select-none">
    <div class="space-y-1">
      <div class="text-xs font-bold text-zinc-900 uppercase tracking-wider flex items-center gap-1.5">
        <FolderKanban class="w-3.5 h-3.5 text-zinc-700" />
        <span>Библиотека компонентов</span>
      </div>
      <p class="text-xs text-zinc-500">
        Выберите объекты для компоновки или нажмите <span class="font-bold text-zinc-800">+</span> для добавления на холст.
      </p>
    </div>

    <!-- Search input -->
    <div class="relative">
      <Search class="w-3.5 h-3.5 text-zinc-400 absolute left-2.5 top-2.5" />
      <input
        v-model="searchQuery"
        @input="loadItems"
        type="text"
        placeholder="Поиск по названию или тегам..."
        class="w-full text-xs pl-8 pr-3 py-1.5 bg-zinc-50 border border-zinc-200 rounded-md focus:outline-none focus:ring-1 focus:ring-zinc-800 focus:bg-white"
      />
    </div>

    <!-- Category filter chips -->
    <div class="flex flex-wrap gap-1">
      <button
        v-for="cat in categories"
        :key="cat.id"
        @click="selectedCategory = cat.id"
        :class="[
          'px-2 py-0.5 text-[11px] font-medium rounded transition',
          selectedCategory === cat.id ? 'bg-zinc-900 text-white' : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
        ]"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- Selected items action bar -->
    <div v-if="selectedKeys.length > 0" class="p-2.5 bg-zinc-50 border border-zinc-300 rounded-md space-y-2">
      <div class="flex items-center justify-between text-xs font-semibold text-zinc-900">
        <span>Выбрано: {{ selectedKeys.length }}</span>
        <button @click="selectedKeys = []" class="text-[11px] text-zinc-500 hover:text-zinc-900 underline">
          Сбросить
        </button>
      </div>

      <div class="grid grid-cols-2 gap-1 bg-zinc-200/60 p-0.5 rounded text-[11px] font-semibold">
        <button
          type="button"
          @click="withBackground = false"
          :class="[!withBackground ? 'bg-white text-zinc-900 shadow-xs' : 'text-zinc-500 hover:text-zinc-900']"
          class="py-1 px-1.5 rounded transition text-center"
        >
          Главные
        </button>
        <button
          type="button"
          @click="withBackground = true"
          :class="[withBackground ? 'bg-white text-zinc-900 shadow-xs' : 'text-zinc-500 hover:text-zinc-900']"
          class="py-1 px-1.5 rounded transition text-center"
        >
          С фоновыми (mono)
        </button>
      </div>

      <div class="flex items-center gap-1.5">
        <select
          v-model="selectedPreset"
          class="text-xs bg-white border border-zinc-200 rounded px-2 py-1 text-zinc-800 flex-1 focus:outline-none"
        >
          <option value="assembled">Собранно</option>
          <option value="shifted">Со смещением</option>
          <option value="under_title">Под заголовок</option>
        </select>

        <button
          @click="handleComposeSelected"
          class="px-2.5 py-1 bg-zinc-900 hover:bg-black text-white text-xs font-semibold rounded transition"
        >
          Собрать
        </button>
      </div>
    </div>

    <!-- Component Grid -->
    <div class="grid grid-cols-2 gap-2 max-h-[400px] overflow-y-auto pr-1">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        :class="[
          'group relative p-2 rounded-md border bg-white flex flex-col items-center justify-between transition-all cursor-pointer',
          selectedKeys.includes(item.key) ? 'border-zinc-900 ring-1 ring-zinc-900' : 'border-zinc-200 hover:border-zinc-300'
        ]"
        @click="toggleSelect(item.key)"
      >
        <!-- Selection checkbox badge -->
        <div
          :class="[
            'absolute top-1.5 left-1.5 w-3.5 h-3.5 rounded border flex items-center justify-center transition-all',
            selectedKeys.includes(item.key) ? 'bg-zinc-900 border-zinc-900 text-white' : 'border-zinc-300 bg-white'
          ]"
        >
          <Check v-if="selectedKeys.includes(item.key)" class="w-2.5 h-2.5 stroke-[3]" />
        </div>

        <!-- Add single directly to canvas -->
        <button
          @click.stop="addSingleToCanvas(item)"
          title="Добавить на холст"
          class="absolute top-1.5 right-1.5 w-5 h-5 rounded bg-zinc-100 group-hover:bg-zinc-900 group-hover:text-white text-zinc-600 flex items-center justify-center transition"
        >
          <Plus class="w-3 h-3" />
        </button>

        <!-- SVG Preview -->
        <div class="w-full h-16 flex items-center justify-center p-1 my-1">
          <img :src="item.svg_path" :alt="item.name" class="max-w-full max-h-full object-contain pointer-events-none" />
        </div>

        <!-- Name & Type badge -->
        <div class="w-full text-center">
          <div class="text-[11px] font-semibold text-zinc-900 truncate">{{ item.name }}</div>
          <div class="text-[9px] text-zinc-400">
            {{ item.type === 'main' ? 'Главный' : 'Фоновый' }} • {{ item.size }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
