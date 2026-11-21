"""
Роутер каталога библиотеки компонентов.

Предоставляет эндпоинты для получения списка доступных векторных объектов,
поиска по тегам и выгрузки исходного SVG кода.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Response
from api.schemas.library import LibraryResponse
from core.logger import get_logger
from services.library_service import LibraryService

router = APIRouter(prefix="/api/v1/library", tags=["Library"])
log = get_logger("api_library")
service = LibraryService()


@router.get("", response_model=LibraryResponse)
async def list_items(
    q: Optional[str] = Query(None, description="Поисковый запрос"),
    size: Optional[str] = Query(None, description="Размер детализации L или S"),
    item_type: Optional[str] = Query(None, description="Тип: main или background"),
):
    """Возвращает список компонентов с возможностью фильтрации."""
    items = service.search(query=q, size=size, item_type=item_type)
    return LibraryResponse(total=len(items), items=items)


@router.get("/{item_id}")
async def get_item(item_id: str):
    """Возвращает метаданные компонента по ID."""
    item = service.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Компонент {item_id} не найден")
    return item


@router.get("/{item_id}/svg")
async def get_item_svg(item_id: str):
    """Возвращает чистый SVG код компонента с Content-Type image/svg+xml."""
    svg = service.get_svg_content(item_id)
    if not svg:
        raise HTTPException(status_code=404, detail="SVG файл не найден")
    return Response(content=svg, media_type="image/svg+xml")
