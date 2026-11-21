"""
Скрипт сборки и индексации библиотеки SVG-компонентов.

Формирует каталог компонентов в форматах L и S, генерирует монохромные
версии для фоновых объектов и создаёт единый data/library/library.json.
"""

import json
import os
import re
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(BASE_DIR, "data", "library", "svg")
OUTPUT_JSON = os.path.join(BASE_DIR, "data", "library", "library.json")

ITEMS_META = {
    "book": {
        "name": "Книга",
        "category": "study",
        "tags": ["книга", "учёба", "образование", "чтение", "знания", "документ", "book", "education", "knowledge"],
    },
    "coin": {
        "name": "Монета",
        "category": "finance",
        "tags": ["монета", "деньги", "финансы", "оплата", "валюта", "инвестиции", "coin", "money", "finance"],
    },
    "folder": {
        "name": "Папка",
        "category": "work",
        "tags": ["папка", "файлы", "документы", "офис", "архив", "проект", "folder", "files", "archive"],
    },
    "headphones": {
        "name": "Наушники",
        "category": "media",
        "tags": ["наушники", "музыка", "звук", "подкаст", "аудио", "отдых", "headphones", "audio", "music"],
    },
    "lamp": {
        "name": "Лампа",
        "category": "study",
        "tags": ["лампа", "свет", "идея", "инсайт", "рабочее место", "вдохновение", "lamp", "light", "idea"],
    },
    "pen": {
        "name": "Ручка",
        "category": "work",
        "tags": ["ручка", "письмо", "договор", "подпись", "заметка", "канцелярия", "pen", "write", "contract"],
    },
    "phone": {
        "name": "Телефон",
        "category": "tech",
        "tags": ["телефон", "смартфон", "связь", "мобильный", "интернет", "приложение", "phone", "mobile", "app"],
    },
    "puzzle": {
        "name": "Пазлы",
        "category": "work",
        "tags": ["пазлы", "логика", "команда", "решение", "структура", "интеграция", "puzzle", "team", "solution"],
    },
    "wallet": {
        "name": "Кошелек",
        "category": "finance",
        "tags": ["кошелек", "деньги", "карты", "банк", "покупки", "бюджет", "wallet", "payments", "budget"],
    },
}


def to_gray_hex(hex_str: str) -> str:
    """
    Конвертирует HEX цвет в мягкий нейтральный оттенок серого.

    Сохраняет контурный цвет #181817 и белые блики неизменными,
    а цветные заливки переводит в градации яркости по формуле ITU-R.
    """
    if hex_str.lower() in ("#181817", "#000000", "black"):
        return "#181817"
    if hex_str.lower() in ("#ffffff", "white", "#f5f5f5"):
        return hex_str
    h = hex_str.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    lum = int(0.299 * r + 0.587 * g + 0.114 * b)
    val = int(185 + (lum / 255.0) * 55)
    return f"#{val:02x}{val:02x}{val:02x}"


def convert_svg_to_mono(content: str) -> str:
    """
    Преобразует цветной SVG в монохромный фоновый SVG.

    Заменяет все шестнадцатеричные цвета заливки и обводки
    на соответствующие нейтральные оттенки.
    """
    def replace_color(match):
        prefix, color = match.group(1), match.group(2)
        return f'{prefix}="{to_gray_hex(color)}"'

    content = re.sub(r'(fill|stroke)="(#[0-9a-fA-F]{6})"', replace_color, content)
    return content


def scale_svg_dimensions(content: str, scale: float = 0.5) -> str:
    """
    Масштабирует атрибуты width и height в корневом теге svg.

    Используется для генерации размеров S из моделей L,
    сохраняя исходный viewBox неизменным для точности векторов.
    """
    w_match = re.search(r'width="([0-9.]+)"', content)
    h_match = re.search(r'height="([0-9.]+)"', content)
    if w_match and h_match:
        new_w = float(w_match.group(1)) * scale
        new_h = float(h_match.group(1)) * scale
        content = re.sub(r'width="[0-9.]+"', f'width="{new_w:.3f}"', content, count=1)
        content = re.sub(r'height="[0-9.]+"', f'height="{new_h:.3f}"', content, count=1)
    return content


def get_svg_dimensions(svg_path: str) -> Tuple[float, float]:
    """
    Извлекает размеры width и height из SVG файла.

    Возвращает кортеж (width, height). При отсутствии атрибутов
    использует значения из viewBox.
    """
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()
    w_match = re.search(r'width="([0-9.]+)"', content)
    h_match = re.search(r'height="([0-9.]+)"', content)
    if w_match and h_match:
        return float(w_match.group(1)), float(h_match.group(1))
    vb_match = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', content)
    if vb_match:
        return float(vb_match.group(1)), float(vb_match.group(2))
    return 300.0, 300.0


def ensure_s_svgs():
    """
    Создаёт недостающие S-версии из L-версий масштабированием в 0.5.

    Гарантирует, что каждый из 9 объектов имеет чистую S-версию.
    """
    for key in ITEMS_META.keys():
        s_file = os.path.join(SVG_DIR, "S", f"{key}.svg")
        l_file = os.path.join(SVG_DIR, "L", f"{key}.svg")
        if not os.path.exists(s_file) and os.path.exists(l_file):
            with open(l_file, "r", encoding="utf-8") as f:
                content = f.read()
            s_content = scale_svg_dimensions(content, 0.5)
            with open(s_file, "w", encoding="utf-8") as f:
                f.write(s_content)


def generate_mono_variants():
    """
    Генерирует монохромные варианты для фоновых объектов L и S.

    Сохраняет файлы в директории svg/L/mono и svg/S/mono.
    """
    for size in ("L", "S"):
        mono_dir = os.path.join(SVG_DIR, size, "mono")
        os.makedirs(mono_dir, exist_ok=True)
        for key in ITEMS_META.keys():
            color_file = os.path.join(SVG_DIR, size, f"{key}.svg")
            mono_file = os.path.join(mono_dir, f"{key}.svg")
            if os.path.exists(color_file):
                with open(color_file, "r", encoding="utf-8") as f:
                    content = f.read()
                mono_content = convert_svg_to_mono(content)
                with open(mono_file, "w", encoding="utf-8") as f:
                    f.write(mono_content)


def build_item_record(key: str, size: str, is_mono: bool) -> Dict:
    """
    Формирует единую структуру описания компонента для каталога.

    Возвращает словарь с метаданными компонента для JSON-индекса.
    """
    meta = ITEMS_META[key]
    suffix = "mono" if is_mono else "color"
    comp_type = "background" if is_mono else "main"
    sub_path = f"{size}/mono/{key}.svg" if is_mono else f"{size}/{key}.svg"
    full_path = os.path.join(SVG_DIR, sub_path)
    w, h = get_svg_dimensions(full_path)
    return {
        "id": f"{key}_{size.lower()}_{suffix}",
        "key": key,
        "name": meta["name"],
        "size": size,
        "type": comp_type,
        "category": meta["category"],
        "tags": meta["tags"],
        "svg_path": f"/library/svg/{sub_path}",
        "width": round(w, 2),
        "height": round(h, 2),
        "aspect_ratio": round(w / h if h else 1.0, 3),
    }


def build_catalog() -> List[Dict]:
    """
    Собирает полный каталог компонентов (все размеры и типы).

    Возвращает список словарей элементов библиотеки.
    """
    items = []
    for key in sorted(ITEMS_META.keys()):
        for size in ("L", "S"):
            # Цветной главный объект
            items.append(build_item_record(key, size, False))
            # Монохромный фоновый объект
            items.append(build_item_record(key, size, True))
    return items


def main():
    """
    Точка входа сборщика библиотеки SVG-элементов.

    Создаёт недостающие файлы и записывает library.json.
    """
    print("Начало сборки библиотеки SVG...")
    ensure_s_svgs()
    generate_mono_variants()
    catalog = build_catalog()
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"✅ Каталог собран! Всего элементов: {len(catalog)}. Файл: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
