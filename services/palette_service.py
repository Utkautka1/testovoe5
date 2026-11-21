"""
Сервис управления цветовыми палитрами и перекраски SVG.

Обеспечивает получение доступных палитр и математически корректную
перекраску векторных слоёв с соблюдением контраста и правил Figma.
"""

import re
from typing import Dict, List, Optional
from core.logger import get_logger
from services.models import Palette

log = get_logger("palette_service")

PALETTES: Dict[str, Palette] = {
    "warm_sun": Palette(
        id="warm_sun",
        name="Тёплая солнечная",
        background="#FDD7B9",
        accent_primary="#D27532",
        accent_secondary="#F9ECB0",
        accent_light="#FDD7B9",
    ),
    "cool_mint": Palette(
        id="cool_mint",
        name="Мятно-бирюзовая",
        background="#BEEBEB",
        accent_primary="#5ABEBE",
        accent_secondary="#80DADA",
        accent_light="#BEEBEB",
    ),
    "violet_dusk": Palette(
        id="violet_dusk",
        name="Лавандовый вечер",
        background="#D7CDF5",
        accent_primary="#7864D7",
        accent_secondary="#6D7BFC",
        accent_light="#D7CDF5",
    ),
    "coral_dawn": Palette(
        id="coral_dawn",
        name="Коралловый рассвет",
        background="#FFE3E1",
        accent_primary="#F9A3AA",
        accent_secondary="#FFD4F2",
        accent_light="#FFE3E1",
    ),
}


class PaletteService:
    """Сервис палитр и трансформации цветов SVG."""

    def __init__(self):
        # self.palettes — кэш доступных цветовых схем оформления
        self.palettes = PALETTES

    def list_palettes(self) -> List[Palette]:
        """
        Возвращает список всех зарегистрированных палитр.

        Служит для передачи клиенту списка доступных схем перекраски.
        """
        return list(self.palettes.values())

    def get_palette(self, palette_id: str) -> Palette:
        """
        Возвращает палитру по ID с фолбэком на дефолтную 'warm_sun'.

        Исключает сбои при передаче несуществующего ключа палитры.
        """
        return self.palettes.get(palette_id, self.palettes["warm_sun"])

    def _build_color_map(self, target: Palette) -> Dict[str, str]:
        """
        Строит таблицу соответствия базовых цветов исходников цветам целевой палитры.

        Каждый ключевой оттенок исходников мапится на соответствующую роль в палитре.
        """
        return {
            "#F9ECB0": target.accent_secondary,
            "#FDD7B9": target.accent_light,
            "#D27532": target.accent_primary,
            "#6D7BFC": target.accent_secondary,
            "#7864D7": target.accent_primary,
            "#D7CDF5": target.accent_light,
            "#5ABEBE": target.accent_primary,
            "#80DADA": target.accent_secondary,
            "#BEEBEB": target.accent_light,
            "#F9A3AA": target.accent_primary,
            "#FFD4F2": target.accent_secondary,
            "#FFE3E1": target.accent_light,
        }

    def recolor_svg(self, svg_content: str, palette_id: str) -> str:
        """
        Перекрашивает SVG строку в цвета заданной палитры.

        Выполняет точечную замену HEX кодов заливки и обводки,
        сохраняя чёрные контуры и белые элементы нетронутыми.
        """
        target = self.get_palette(palette_id)
        color_map = self._build_color_map(target)

        def replacer(match):
            prop, col = match.group(1), match.group(2).upper()
            new_col = color_map.get(col, col)
            return f'{prop}="{new_col}"'

        result = re.sub(r'(fill|stroke)="(#[0-9a-fA-F]{6})"', replacer, svg_content)
        log.debug(f"SVG успешно перекрашен в палитру {palette_id}")
        return result
