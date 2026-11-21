import { fabric } from 'fabric'
import type { BackgroundLine, CanvasFormat, ElementSize, Palette, PlacedElement } from '../types'
import { fetchSvgCode } from '../api/client'

export interface ExtendedFabricObject extends fabric.Group {
  elementKey?: string
  elementSize?: ElementSize
  isBackground?: boolean
  originalColors?: Map<fabric.Object, string>
}

export class FabricService {
  private canvas: fabric.Canvas | null = null
  private currentPalette: Palette | null = null

  public init(canvasEl: HTMLCanvasElement, width: number, height: number, bgColor = '#FDD7B9') {
    this.canvas = new fabric.Canvas(canvasEl, {
      width,
      height,
      backgroundColor: bgColor,
      preserveObjectStacking: true,
      selection: true,
    })
    return this.canvas
  }

  public getCanvas(): fabric.Canvas | null {
    return this.canvas
  }

  public setDimensions(width: number, height: number) {
    if (!this.canvas) return
    this.canvas.setWidth(width)
    this.canvas.setHeight(height)
    this.canvas.renderAll()
  }

  public setBackgroundColor(color: string) {
    if (!this.canvas) return
    this.canvas.setBackgroundColor(color, () => this.canvas?.renderAll())
  }

  public clear() {
    if (!this.canvas) return
    this.canvas.clear()
    if (this.currentPalette) {
      this.setBackgroundColor(this.currentPalette.background)
    }
  }

  public deleteSelected() {
    if (!this.canvas) return
    const active = this.canvas.getActiveObjects()
    if (active.length > 0) {
      this.canvas.discardActiveObject()
      active.forEach(obj => this.canvas?.remove(obj))
      this.canvas.requestRenderAll()
    }
  }

  public bringForward() {
    if (!this.canvas) return
    const active = this.canvas.getActiveObject()
    if (active) {
      this.canvas.bringForward(active)
      this.canvas.requestRenderAll()
    }
  }

  public sendBackward() {
    if (!this.canvas) return
    const active = this.canvas.getActiveObject()
    if (active) {
      this.canvas.sendBackwards(active)
      this.canvas.requestRenderAll()
    }
  }

  public duplicateSelected() {
    if (!this.canvas) return
    const active = this.canvas.getActiveObject()
    if (!active) return
    active.clone((cloned: fabric.Object) => {
      this.canvas?.discardActiveObject()
      cloned.set({
        left: (cloned.left || 0) + 30,
        top: (cloned.top || 0) + 30,
        evented: true,
      })
      this.canvas?.add(cloned)
      this.canvas?.setActiveObject(cloned)
      this.canvas?.requestRenderAll()
    })
  }

  public async toggleActiveObjectBackgroundState(): Promise<boolean> {
    if (!this.canvas) return false
    const active = this.canvas.getActiveObject() as ExtendedFabricObject
    if (!active || !active.elementKey || !active.elementSize) return false
    const newIsBg = !active.isBackground
    const path = `/library/svg/${active.elementSize}/${newIsBg ? 'mono/' : ''}${active.elementKey}.svg`
    const svgCode = await fetchSvgCode(path)
    return new Promise(resolve => {
      fabric.loadSVGFromString(svgCode, (objects, options) => {
        if (!objects || !this.canvas) return resolve(false)
        const group: ExtendedFabricObject = new fabric.Group(objects, options)
        group.set({
          left: active.left,
          top: active.top,
          scaleX: active.scaleX,
          scaleY: active.scaleY,
          angle: active.angle,
          originX: 'left',
          originY: 'top',
        })
        group.elementKey = active.elementKey
        group.elementSize = active.elementSize
        group.isBackground = newIsBg
        this.recordOriginalColors(group)
        if (this.currentPalette && !newIsBg) {
          this.applyPaletteToObject(group, this.currentPalette)
        }
        this.canvas.remove(active)
        this.canvas.add(group)
        this.canvas.setActiveObject(group)
        this.canvas.requestRenderAll()
        resolve(true)
      })
    })
  }

  private recordOriginalColors(group: ExtendedFabricObject) {
    group.originalColors = new Map()
    group.getObjects().forEach(child => {
      const fill = (child.fill as string) || ''
      if (fill.startsWith('#')) {
        group.originalColors?.set(child, fill.toUpperCase())
      }
    })
  }

  private configureGroup(group: ExtendedFabricObject, p: PlacedElement, size: ElementSize) {
    group.set({
      left: p.x,
      top: p.y,
      scaleX: p.scale_x,
      scaleY: p.scale_y,
      angle: p.rotation,
      originX: 'left',
      originY: 'top',
    })
    group.elementKey = p.key
    group.elementSize = size
    group.isBackground = p.is_background
    this.recordOriginalColors(group)
  }

  public async loadElement(p: PlacedElement, size: ElementSize): Promise<ExtendedFabricObject> {
    const svgCode = await fetchSvgCode(p.svg_path)
    return new Promise((resolve, reject) => {
      fabric.loadSVGFromString(svgCode, (objects, options) => {
        if (!objects || objects.length === 0) {
          return reject(new Error(`Failed to parse SVG for ${p.key}`))
        }
        const group: ExtendedFabricObject = new fabric.Group(objects, options)
        this.configureGroup(group, p, size)
        this.canvas?.add(group)
        if (this.currentPalette && !p.is_background) {
          this.applyPaletteToObject(group, this.currentPalette)
        }
        this.canvas?.requestRenderAll()
        resolve(group)
      })
    })
  }

  private renderBackgroundDecoration(lines: BackgroundLine[] | undefined, palette: Palette) {
    if (!this.canvas) return
    const w = this.canvas.getWidth()
    const h = this.canvas.getHeight()
    if (lines && lines.length > 0) {
      for (const line of lines) {
        const fLine = new fabric.Line([line.x, line.y + line.h, line.x + line.w, line.y], {
          stroke: palette.accent_primary,
          strokeWidth: 1.5,
          opacity: 0.25,
          selectable: false,
          evented: false,
        })
        this.canvas.add(fLine)
      }
    }
    const dot1 = new fabric.Circle({
      left: w * 0.08,
      top: h * 0.78,
      radius: 14,
      fill: palette.accent_primary,
      opacity: 0.35,
      selectable: false,
      evented: false,
    })
    const dot2 = new fabric.Circle({
      left: w * 0.08 + 18,
      top: h * 0.78 + 4,
      radius: 14,
      fill: '#FFFFFF',
      opacity: 0.85,
      selectable: false,
      evented: false,
    })
    this.canvas.add(dot1)
    this.canvas.add(dot2)
  }

  public async renderComposition(
    elements: PlacedElement[],
    size: ElementSize,
    palette: Palette,
    backgroundLines?: BackgroundLine[]
  ) {
    this.clear()
    this.currentPalette = palette
    this.setBackgroundColor(palette.background)
    this.renderBackgroundDecoration(backgroundLines, palette)
    const sorted = [...elements].sort((a, b) => a.z_index - b.z_index)
    for (const el of sorted) {
      await this.loadElement(el, size)
    }
  }

  private mapColorToPalette(origColor: string, palette: Palette): string {
    const map: Record<string, string> = {
      '#F9ECB0': palette.accent_secondary,
      '#FDD7B9': palette.accent_light,
      '#D27532': palette.accent_primary,
      '#6D7BFC': palette.accent_secondary,
      '#7864D7': palette.accent_primary,
      '#D7CDF5': palette.accent_light,
      '#5ABEBE': palette.accent_primary,
      '#80DADA': palette.accent_secondary,
      '#BEEBEB': palette.accent_light,
      '#F9A3AA': palette.accent_primary,
      '#FFD4F2': palette.accent_secondary,
      '#FFE3E1': palette.accent_light,
    }
    return map[origColor] || origColor
  }

  public applyPaletteToObject(group: ExtendedFabricObject, palette: Palette) {
    if (!group.originalColors || group.isBackground) return
    group.getObjects().forEach(child => {
      const orig = group.originalColors?.get(child)
      if (orig) {
        const newColor = this.mapColorToPalette(orig, palette)
        child.set('fill', newColor)
      }
    })
  }

  public applyPalette(palette: Palette) {
    if (!this.canvas) return
    this.currentPalette = palette
    this.setBackgroundColor(palette.background)
    this.canvas.getObjects().forEach(obj => {
      this.applyPaletteToObject(obj as ExtendedFabricObject, palette)
    })
    this.canvas.requestRenderAll()
  }

  public exportSVG(): string {
    if (!this.canvas) return ''
    return this.canvas.toSVG({
      suppressPreamble: false,
      viewBox: {
        x: 0,
        y: 0,
        width: this.canvas.getWidth(),
        height: this.canvas.getHeight(),
      },
    })
  }

  public downloadSVG(filename = 'illustration.svg') {
    const svgData = this.exportSVG()
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }
}

export const fabricService = new FabricService()
