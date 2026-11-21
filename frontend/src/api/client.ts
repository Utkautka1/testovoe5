import type { CanvasFormat, CompositionPlan, ElementSize, LayoutPreset, LibraryItem, Palette } from '../types'

const API_BASE = '/api/v1'

export async function fetchLibrary(query?: string, size?: ElementSize): Promise<LibraryItem[]> {
  const params = new URLSearchParams()
  if (query) params.append('q', query)
  if (size) params.append('size', size)
  const res = await fetch(`${API_BASE}/library?${params.toString()}`)
  if (!res.ok) throw new Error('Failed to fetch library items')
  const data = await res.json()
  return data.items
}

export async function fetchPalettes(): Promise<Palette[]> {
  const res = await fetch(`${API_BASE}/palettes`)
  if (!res.ok) throw new Error('Failed to fetch palettes')
  const data = await res.json()
  return data.palettes
}

export async function requestAIComposition(
  prompt: string,
  format: CanvasFormat,
  size: ElementSize,
  includeBackground = false
): Promise<CompositionPlan> {
  const res = await fetch(`${API_BASE}/compose/ai`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, format, size, include_background: includeBackground }),
  })
  if (!res.ok) throw new Error('Failed to generate AI composition')
  const data = await res.json()
  return data.plan
}

export async function requestManualComposition(
  elementKeys: string[],
  format: CanvasFormat,
  preset: LayoutPreset,
  size: ElementSize,
  paletteId: string,
  includeBackground = false,
  archetypeId?: string
): Promise<CompositionPlan> {
  const res = await fetch(`${API_BASE}/compose/manual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      element_keys: elementKeys,
      archetype_id: archetypeId,
      format,
      preset,
      size,
      palette_id: paletteId,
      include_background: includeBackground,
    }),
  })
  if (!res.ok) throw new Error('Failed to compose layout')
  const data = await res.json()
  return data.plan
}

export async function fetchSvgCode(svgPath: string): Promise<string> {
  const res = await fetch(svgPath)
  if (!res.ok) throw new Error(`Failed to load SVG: ${svgPath}`)
  return res.text()
}
