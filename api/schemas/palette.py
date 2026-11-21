"""
Схемы для эндпоинтов управления палитрами.
"""

from typing import List
from pydantic import BaseModel
from services.models import Palette


class PaletteListResponse(BaseModel):
    """Схема ответа со списком цветовых палитр."""
    total: int
    palettes: List[Palette]


class RecolorRequest(BaseModel):
    """Схема запроса на перекраску SVG."""
    svg_content: str
    palette_id: str


class RecolorResponse(BaseModel):
    """Схема ответа с перекрашенным SVG."""
    palette_id: str
    recolored_svg: str
