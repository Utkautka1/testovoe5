# UML Архитектура проекта: Vector Illustration Composer

Диаграмма архитектуры и взаимодействия компонентов системы генерации векторных композиций по спецификации Figma Section 1.

```mermaid
classDiagram
    direction TB

    class Settings {
        +str deepseek_api_key
        +str deepseek_base_url
        +str deepseek_model
        +str api_host
        +int api_port
        +bool api_debug
        +List~str~ cors_origins
        +str library_data_path
        +str svg_assets_dir
        +get_settings() Settings
    }

    class LibraryService {
        -Settings settings
        -List~dict~ _catalog
        -Dict~str, dict~ _by_id
        +get_all() List~dict~
        +get_by_id(item_id) dict
        +search(query, size, item_type) List~dict~
        +get_svg_content(item_id) str
    }

    class CompositionService {
        -LibraryService library
        -dict scenes_data
        +compose(element_keys, fmt, preset, size, palette_id, include_bg, archetype_id) CompositionPlan
        -_load_scenes(path) dict
        -_resolve_archetype(keys, include_bg, explicit_id) str
        -_get_scene_data(fmt, archetype) dict
        -_build_placed_element(obj, size, z_index, is_bg) PlacedElement
        -_generate_elements(scene, size, include_bg) List~PlacedElement~
        -_extract_background_lines(scene) List~BackgroundLine~
    }

    class DeepSeekService {
        -Settings settings
        -AsyncClient client
        +analyze_metaphor(prompt) dict
        -_post_chat_completion(prompt) str
        -_parse_and_validate(raw) dict
        -_fallback_match(prompt) dict
    }

    class PaletteService {
        -Dict~str, Palette~ palettes
        +list_palettes() List~Palette~
        +get_palette(palette_id) Palette
        +recolor_svg(svg_content, palette_id) str
        -_build_color_map(target) Dict~str, str~
    }

    class FabricService {
        -Canvas canvas
        -Palette currentPalette
        +init(canvasEl, width, height, bgColor) Canvas
        +setDimensions(width, height) void
        +loadElement(placedElement, size) ExtendedFabricObject
        +renderComposition(elements, size, palette, backgroundLines) void
        +renderBackgroundDecoration(lines, palette) void
        +applyPalette(palette) void
        +toggleActiveObjectBackgroundState() Promise~bool~
        +exportSVG() str
        +downloadSVG(filename) void
    }

    class BackgroundLine {
        +str name
        +float x
        +float y
        +float w
        +float h
    }

    class PlacedElement {
        +str element_id
        +str key
        +float x
        +float y
        +float scale_x
        +float scale_y
        +float rotation
        +int z_index
        +bool is_background
        +str svg_path
        +float width
        +float height
    }

    class CompositionPlan {
        +CanvasFormat format
        +LayoutPreset preset
        +ElementSize size
        +str palette_id
        +List~PlacedElement~ elements
        +List~BackgroundLine~ background_lines
        +str explanation
    }

    class Palette {
        +str id
        +str name
        +str background
        +str accent_primary
        +str accent_secondary
        +str accent_light
    }

    CompositionService --> LibraryService : использует каталог
    CompositionService ..> CompositionPlan : создаёт
    CompositionPlan *-- PlacedElement : содержит объекты
    CompositionPlan *-- BackgroundLine : содержит линии стола
    DeepSeekService ..> Settings : загружает конфигурацию
    PaletteService ..> Palette : управляет
    FabricService ..> PlacedElement : визуализирует
    FabricService ..> BackgroundLine : отрисовывает линии стола
    FabricService ..> Palette : перекрашивает
```

---

## Ключевые компоненты архитектуры:

1. **`CompositionService` (Services/Layout Engine):**
   - 100% совпадение с Section 1 Figma макета:
     - 6 канонических архетипов в 3 форматах (всего 18 сцен):
       - *Ряд 1 («Только главные»):* `phone_puzzle`, `book_phone`, `folder_wallet_coin`.
       - *Ряд 2 («С фоновыми»):* `vase_headphones` (ваза mono), `lamp_wallet_coin` (лампа mono), `book_puzzle_pen` (книга mono).
     - Попиксельная привязка к левому верхнему углу (`originX: left, originY: top`).
     - Натуральный масштаб элементов ($1.0$).
     - Отрисовка изометрических линий стола (угол $30^\circ$) и декоративных конфетти.

2. **`FabricService` (Frontend Canvas Controller):**
   - Инкапсулирует работу с Fabric.js и SVG DOM.
   - Поддерживает переключение состояния активного объекта `Главный ⇄ Фоновый` в реальном времени.
   - Семантическая перекраска по палитрам Figma.
   - Экспорт в чистый векторный SVG вместе с фоновыми направляющими.

3. **`DeepSeekService` (Metaphor Semantic Engine):**
   - Анализирует свободный текстовый бриф пользователя.
   - Автоматически сопоставляет запрос с подходящим каноническим архетипом.
   - Поддерживает все 10 объектов библиотеки, включая вазу с тюльпанами (`vase`).
