"""
Роутер работы с цветовыми палитрами.

Предоставляет перечень доступных палитр и выполняет перекраску SVG.
"""

from fastapi import APIRouter
from api.schemas.palette import PaletteListResponse, RecolorRequest, RecolorResponse
from core.logger import get_logger
from services.palette_service import PaletteService

router = APIRouter(prefix="/api/v1/palettes", tags=["Palettes"])
log = get_logger("api_palettes")
palette_svc = PaletteService()


@router.get("", response_model=PaletteListResponse)
async def list_palettes():
    """Возвращает список всех зарегистрированных цветовых схем."""
    items = palette_svc.list_palettes()
    return PaletteListResponse(total=len(items), palettes=items)


@router.post("/recolor", response_model=RecolorResponse)
async def recolor_svg(req: RecolorRequest):
    """Перекрашивает переданный SVG код в цвета выбранной палитры."""
    recolored = palette_svc.recolor_svg(req.svg_content, req.palette_id)
    return RecolorResponse(palette_id=req.palette_id, recolored_svg=recolored)
