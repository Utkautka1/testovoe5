"""
Схемы запросов и ответов для библиотеки компонентов.
"""

from typing import List, Optional
from pydantic import BaseModel


class LibraryItemDTO(BaseModel):
    """Схема единичного компонента в библиотеке."""
    id: str
    key: str
    name: str
    size: str
    type: str
    category: str
    tags: List[str]
    svg_path: str
    width: float
    height: float
    aspect_ratio: float


class LibraryResponse(BaseModel):
    """Ответ со списком компонентов библиотеки."""
    total: int
    items: List[LibraryItemDTO]
