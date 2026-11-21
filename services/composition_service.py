"""
Сервис расчёта композиционных сеток и координат элементов.

Вычисляет точные пространственные параметры (координаты, масштаб, z-index)
для выбранного набора компонентов, формата холста и шаблона компоновки.
Строго соблюдает каноны Figma Section 1: 100% совпадение с эталонными карточками,
правильные пропорции, слои и монохромные фоновые состояния.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from core.logger import get_logger
from services.library_service import LibraryService
from services.models import (
    BackgroundLine,
    CanvasFormat,
    CompositionPlan,
    ElementSize,
    LayoutPreset,
    PlacedElement,
)

log = get_logger("composition_service")

# Фоновые монохромные объекты в сценах второго ряда
BACKGROUND_OBJECT_KEYS = {"vase", "lamp", "book"}


class CompositionService:
    """Сервис математической компоновки и расчёта координат объектов."""

    def __init__(self, library_service: LibraryService, scenes_path: str = "data/canonical_scenes.json"):
        # library_service — сервис доступа к метаданным компонентов
        self.library = library_service
        # scenes_data — карта 18 канонических композиций из Figma Section 1
        self.scenes_data = self._load_scenes(scenes_path)

    def _load_scenes(self, path: str) -> dict:
        """Загружает базу канонических координат Section 1 из JSON-файла."""
        if not os.path.exists(path):
            log.warning(f"Файл {path} не найден, используется пустая база сцен")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _resolve_archetype(self, keys: List[str], include_bg: bool, explicit_id: Optional[str] = None) -> str:
        """Определяет канонический архетип композиции по явным ключам или смыслу."""
        if explicit_id:
            return explicit_id
        kset = set(keys)
        if include_bg:
            if "headphones" in kset or "vase" in kset:
                return "vase_headphones"
            if "wallet" in kset or "coin" in kset or "lamp" in kset:
                return "lamp_wallet_coin"
            if "pen" in kset or "puzzle" in kset or "book" in kset:
                return "book_puzzle_pen"
            return "vase_headphones"
        if "wallet" in kset or "coin" in kset or "folder" in kset:
            return "folder_wallet_coin"
        if "book" in kset:
            return "book_phone"
        return "phone_puzzle"

    def _get_scene_data(self, fmt: CanvasFormat, archetype: str) -> dict:
        """Извлекает спецификацию сцены для заданного формата холста."""
        fmt_key = fmt.value
        fmt_scenes = self.scenes_data.get(fmt_key, {})
        if archetype in fmt_scenes:
            return fmt_scenes[archetype]
        # Резервный поиск по первому доступному формату
        for f_scenes in self.scenes_data.values():
            if archetype in f_scenes:
                return f_scenes[archetype]
        return {}

    def _build_placed_element(
        self, obj: dict, size: ElementSize, z_index: int, is_bg: bool
    ) -> Optional[PlacedElement]:
        """Загружает метаданные компонента и строит PlacedElement."""
        key = obj["key"]
        t_suf = "mono" if is_bg else "color"
        item = self.library.get_by_id(f"{key}_{size.lower()}_{t_suf}") or self.library.get_by_id(f"{key}_{size.lower()}_color")
        if not item:
            return None
        scale = 0.5 if size == ElementSize.S else 1.0
        return PlacedElement(
            element_id=f"{key}_{z_index}", key=key,
            x=round(obj["x"] * scale, 2), y=round(obj["y"] * scale, 2),
            scale_x=scale, scale_y=scale, rotation=0.0, z_index=z_index,
            is_background=is_bg, svg_path=item["svg_path"],
            width=float(item["width"]), height=float(item["height"]),
        )

    def _generate_elements(self, scene: dict, size: ElementSize, include_bg: bool) -> List[PlacedElement]:
        """Генерирует упорядоченный список объектов сцены со слоями z-index."""
        raw_objs = scene.get("objects", [])
        is_scene_bg = include_bg or bool(scene.get("is_background", False))
        elements = []
        for idx, obj in enumerate(raw_objs, start=1):
            key = obj["key"]
            is_bg = (key in BACKGROUND_OBJECT_KEYS) if is_scene_bg else False
            z = 1 if is_bg else (idx + 1)
            el = self._build_placed_element(obj, size, z, is_bg)
            if el:
                elements.append(el)
        elements.sort(key=lambda e: e.z_index)
        return elements

    def _extract_background_lines(self, scene: dict) -> List[BackgroundLine]:
        """Формирует список фоновых изометрических линий стола из макета."""
        raw_lines = scene.get("lines", [])
        lines = []
        for line in raw_lines:
            lines.append(
                BackgroundLine(
                    name=line.get("name", "Line"),
                    x=line["x"],
                    y=line["y"],
                    w=line["w"],
                    h=line["h"],
                )
            )
        return lines

    def compose(
        self,
        element_keys: List[str],
        fmt: CanvasFormat = CanvasFormat.HORIZONTAL_1200_630,
        preset: LayoutPreset = LayoutPreset.ASSEMBLED,
        size: ElementSize = ElementSize.L,
        palette_id: str = "violet_dusk",
        include_bg_elements: bool = False,
        archetype_id: Optional[str] = None,
    ) -> CompositionPlan:
        """Строит каноническую композицию по спецификации Figma Section 1."""
        arch = self._resolve_archetype(element_keys, include_bg_elements, archetype_id)
        scene = self._get_scene_data(fmt, arch)
        elements = self._generate_elements(scene, size, include_bg_elements)
        lines = self._extract_background_lines(scene)
        log.info(f"✅ Композиция сформирована: архетип={arch}, объектов={len(elements)}")
        return CompositionPlan(
            format=fmt, preset=preset, size=size, palette_id=palette_id,
            elements=elements, background_lines=lines,
        )
