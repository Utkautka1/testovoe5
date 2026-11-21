"""
Сервис доступа к библиотеке SVG-компонентов.

Загружает индексированный каталог library.json, кэширует его в памяти
и предоставляет методы фильтрации, поиска и получения сырого SVG-кода.
"""

import json
import os
from typing import Dict, List, Optional
from config import get_settings
from core.logger import get_logger

log = get_logger("library_service")


class LibraryService:
    """Сервис управления каталогом векторных компонентов."""

    def __init__(self):
        # self.settings — глобальные настройки путей к данным
        self.settings = get_settings()
        # self._catalog — кэшированный список словарей элементов
        self._catalog: List[Dict] = []
        # self._by_id — словарь элементов по ключу id для быстрого O(1) доступа
        self._by_id: Dict[str, Dict] = {}
        self._load_catalog()

    def _load_catalog(self):
        """
        Загружает JSON каталог с диска и индексирует его по ID.

        При отсутствии файла логирует ошибку и оставляет кэш пустым.
        """
        path = self.settings.library_data_path
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._catalog = json.load(f)
            self._by_id = {item["id"]: item for item in self._catalog}
            log.info(f"✅ Библиотека загружена: {len(self._catalog)} компонентов")
        except Exception as e:
            log.error(f"❌ Ошибка загрузки каталога {path}: {e}")
            self._catalog, self._by_id = [], {}

    def get_all(self) -> List[Dict]:
        """
        Возвращает полный каталог элементов библиотеки.

        Используется клиентским интерфейсом для отображения бокового меню.
        """
        return self._catalog

    def get_by_id(self, item_id: str) -> Optional[Dict]:
        """
        Возвращает метаданные компонента по его точному ID.

        Возвращает None, если элемент с таким ID не зарегистрирован.
        """
        return self._by_id.get(item_id)

    def search(
        self,
        query: Optional[str] = None,
        size: Optional[str] = None,
        item_type: Optional[str] = None,
    ) -> List[Dict]:
        """
        Ищет элементы по ключевым словам, размеру детализации и типу.

        Сравнивает подстроку с именем компонента и списком семантических тегов.
        """
        q = (query or "").strip().lower()
        results = []
        for item in self._catalog:
            if size and item["size"] != size:
                continue
            if item_type and item["type"] != item_type:
                continue
            if q and not (q in item["name"].lower() or any(q in t for t in item["tags"])):
                continue
            results.append(item)
        return results

    def get_svg_content(self, item_id: str) -> Optional[str]:
        """
        Считывает сырой контент SVG файла компонента с диска.

        Возвращает строку XML разметки SVG или None при ошибке чтения.
        """
        item = self.get_by_id(item_id)
        if not item:
            return None
        rel_path = item["svg_path"].lstrip("/")
        if rel_path.startswith("library/"):
            rel_path = "data/" + rel_path
        full_path = os.path.join(os.getcwd(), rel_path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            log.error(f"Ошибка чтения SVG {full_path}: {e}")
            return None
