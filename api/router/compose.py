"""
Роутер сборки и генерации композиций.

Реализует два сценария:
1. Автоматический AI-подбор и компоновка по метафоре.
2. Ручная компоновка по явно переданному списку объектов.
"""

from fastapi import APIRouter
from api.schemas.compose import AIComposeRequest, ComposeResponse, ManualComposeRequest
from core.logger import get_logger
from services.composition_service import CompositionService
from services.deepseek_service import DeepSeekService
from services.library_service import LibraryService
from services.models import LayoutPreset

router = APIRouter(prefix="/api/v1/compose", tags=["Compose"])
log = get_logger("api_compose")

lib_svc = LibraryService()
comp_svc = CompositionService(lib_svc)
ai_svc = DeepSeekService()


@router.post("/ai", response_model=ComposeResponse)
async def compose_by_ai(req: AIComposeRequest):
    """
    Сценарий 1: Генерация композиции на основе метафоры/заголовка через DeepSeek.
    """
    analysis = await ai_svc.analyze_metaphor(req.prompt)
    preset_enum = LayoutPreset(analysis.get("preset", "assembled"))
    plan = comp_svc.compose(
        element_keys=analysis["selected_keys"],
        fmt=req.format,
        preset=preset_enum,
        size=req.size,
        palette_id=analysis.get("palette_id", "warm_sun"),
        include_bg_elements=req.include_background,
    )
    plan.explanation = analysis.get("explanation")
    return ComposeResponse(success=True, plan=plan)


@router.post("/manual", response_model=ComposeResponse)
async def compose_manual(req: ManualComposeRequest):
    """
    Сценарий 2: Ручная сборка композиции из выбранного списка компонентов.
    """
    plan = comp_svc.compose(
        element_keys=req.element_keys,
        fmt=req.format,
        preset=req.preset,
        size=req.size,
        palette_id=req.palette_id,
        include_bg_elements=req.include_background,
        archetype_id=req.archetype_id,
    )
    return ComposeResponse(success=True, plan=plan)
