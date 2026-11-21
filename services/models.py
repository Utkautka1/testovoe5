"""
Модели данных предметной области (Domain Models & DTO).

Определяют контракты данных для сервисов композиции,
семантического анализа и управления цветовыми палитрами.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class CanvasFormat(str, Enum):
    """Поддерживаемые форматы пропорций холста."""
    HORIZONTAL_1200_630 = "1200x630"
    SQUARE_1000_1000 = "1000x1000"
    VERTICAL_800_1200 = "800x1200"


class LayoutPreset(str, Enum):
    """Типовые композиционные шаблоны размещения объектов."""
    ASSEMBLED = "assembled"          # Собранно (центрированная группа)
    SHIFTED = "shifted"              # Со смещением (динамичный сдвиг)
    UNDER_TITLE = "under_title"      # Под заголовок (свободное место для текста)


class ElementSize(str, Enum):
    """Размер детализации элементов."""
    L = "L"
    S = "S"


class BackgroundLine(BaseModel):
    """Изометрическая линия стола или декоративный штрих фона."""
    name: str
    x: float
    y: float
    w: float
    h: float


class PlacedElement(BaseModel):
    """Размещённый объект на холсте с пространственными параметрами."""
    # element_id — уникальный идентификатор конкретного экземпляра на холсте
    element_id: str
    # key — базовый ключ объекта из каталога (например 'lamp')
    key: str
    # x, y — координаты объекта на холсте (пиксели, привязка left-top)
    x: float
    y: float
    # scale_x, scale_y — коэффициенты масштабирования
    scale_x: float = 1.0
    scale_y: float = 1.0
    # rotation — угол поворота в градусах
    rotation: float = 0.0
    # z_index — порядок наложения слоя (0 — самый нижний)
    z_index: int = 0
    # is_background — флаг фонового монохромного объекта
    is_background: bool = False
    # svg_path — путь к SVG файлу для загрузки
    svg_path: str
    # width, height — естественные габариты исходного SVG
    width: float
    height: float


class CompositionPlan(BaseModel):
    """Итоговый план собранной векторной композиции."""
    # format — формат пропорций холста
    format: CanvasFormat
    # preset — выбранный шаблон компоновки
    preset: LayoutPreset
    # size — детализация элементов (S или L)
    size: ElementSize
    # palette_id — ID рекомендуемой цветовой палитры
    palette_id: str
    # elements — упорядоченный список размещённых объектов
    elements: List[PlacedElement]
    # background_lines — изометрические направляющие линии фона
    background_lines: Optional[List[BackgroundLine]] = None
    # explanation — обоснование AI почему выбраны именно эти объекты
    explanation: Optional[str] = None


class Palette(BaseModel):
    """Цветовая схема оформления иллюстрации."""
    # id — уникальный идентификатор палитры
    id: str
    # name — отображаемое название палитры
    name: str
    # background — цвет фона холста
    background: str
    # accent_primary — главный акцентный цвет
    accent_primary: str
    # accent_secondary — дополнительный акцентный цвет
    accent_secondary: str
    # accent_light — светлый пастельный оттенок
    accent_light: str
    # neutral_dark — цвет контуров (стандартно #181817)
    neutral_dark: str = "#181817"
