export type CanvasFormat = '1200x630' | '1000x1000' | '800x1200'
export type LayoutPreset = 'assembled' | 'shifted' | 'under_title'
export type ElementSize = 'L' | 'S'

export interface LibraryItem {
  id: string
  key: string
  name: string
  size: ElementSize
  type: 'main' | 'background'
  category: string
  tags: string[]
  svg_path: string
  width: number
  height: number
  aspect_ratio: number
}

export interface PlacedElement {
  element_id: string
  key: string
  x: number
  y: number
  scale_x: number
  scale_y: number
  rotation: number
  z_index: number
  is_background: boolean
  svg_path: string
  width: number
  height: number
}

export interface BackgroundLine {
  name: string
  x: number
  y: number
  w: number
  h: number
}

export interface CompositionPlan {
  format: CanvasFormat
  preset: LayoutPreset
  size: ElementSize
  palette_id: string
  elements: PlacedElement[]
  background_lines?: BackgroundLine[]
  explanation?: string
}

export interface Palette {
  id: string
  name: string
  background: string
  accent_primary: string
  accent_secondary: string
  accent_light: string
  neutral_dark: string
}
