"""
Схемы запросов и ответов для эндпоинтов композиции.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from services.models import CanvasFormat, CompositionPlan, ElementSize, LayoutPreset


class AIComposeRequest(BaseModel):
    """Схема запроса на автоматическую сборку композиции по метафоре."""
    # prompt — заголовок или метафора пользователя
    prompt: str = Field(..., min_length=1, max_length=500)
    # format — целевой формат холста
    format: CanvasFormat = CanvasFormat.HORIZONTAL_1200_630
    # size — размер деталей (S или L)
    size: ElementSize = ElementSize.L
    # include_background — добавлять ли фоновый монохромный объект
    include_background: bool = False


class ManualComposeRequest(BaseModel):
    """Схема запроса на сборку композиции по выбранным пользователем объектам."""
    # element_keys — список ключей компонентов (например ['lamp', 'book'])
    element_keys: List[str] = Field(default_factory=list, max_length=10)
    # archetype_id — прямой идентификатор канонической сцены из Section 1
    archetype_id: Optional[str] = None
    # format — формат пропорций холста
    format: CanvasFormat = CanvasFormat.HORIZONTAL_1200_630
    # preset — шаблон компоновки
    preset: LayoutPreset = LayoutPreset.ASSEMBLED
    # size — размер деталей
    size: ElementSize = ElementSize.L
    # palette_id — цветовая схема
    palette_id: str = "warm_sun"
    # include_background — добавлять ли фоновый монохромный объект
    include_background: bool = False


class ComposeResponse(BaseModel):
    """Единая схема ответа с планом композиции."""
    # success — статус успешности операции
    success: bool = True
    # plan — рассчитанный план композиции
    plan: CompositionPlan
