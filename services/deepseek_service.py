"""
Сервис интеграции с DeepSeek API для семантического анализа метафор.

Анализирует текст пользователя, подбирает релевантные объекты из доступных
в библиотеке, определяет пресет компоновки и цветовую палитру.
"""

import json
from typing import Dict, List, Optional
import httpx
from config import get_settings
from core.logger import get_logger

log = get_logger("deepseek_service")

SYSTEM_PROMPT = """Ты — Senior Art Director векторных иллюстраций.
Пользователь передаёт метафору, тему или заголовок.
Твоя задача — выбрать от 2 до 4 объектов строго из разрешённого списка:
- book (книга, учёба, знания)
- coin (монета, деньги, финансы, инвестиции)
- folder (папка, документы, проекты, файлы)
- headphones (наушники, звук, отдых, подкасты, медиа)
- lamp (лампа, свет, идеи, инсайт, мышление)
- pen (ручка, письмо, подписание, договор)
- phone (телефон, технологии, связь, мобильность)
- puzzle (пазлы, команда, решение, интеграция, логика)
- vase (ваза с тюльпанами, эстетика, офис, уют, декор)
- wallet (кошелек, платежи, бюджет, накопления)

Выбери пресет компоновки: "assembled" | "shifted" | "under_title".
Выбери палитру: "warm_sun" | "cool_mint" | "violet_dusk" | "coral_dawn".

Отвечай строго валидным JSON без markdown:
{
  "selected_keys": ["ключ1", "ключ2"],
  "preset": "assembled",
  "palette_id": "warm_sun",
  "explanation": "краткое пояснение на русском (1-2 предложения)"
}"""


class DeepSeekService:
    """Сервис семантического анализа заголовков через DeepSeek API."""

    def __init__(self):
        # settings — конфигурационные параметры доступа к API
        self.settings = get_settings()
        # client — асинхронный HTTP-клиент с таймаутом
        self.client = httpx.AsyncClient(timeout=15.0)

    async def _post_chat_completion(self, user_prompt: str) -> Optional[str]:
        """Отправляет HTTP запрос к DeepSeek chat completions API."""
        url = f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.settings.deepseek_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        resp = await self.client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _parse_and_validate(self, raw_content: str) -> Dict:
        """Парсит JSON ответ модели и отсекает недопустимые ключи."""
        parsed = json.loads(raw_content)
        allowed = {"book", "coin", "folder", "headphones", "lamp", "pen", "phone", "puzzle", "vase", "wallet"}
        keys = [k for k in parsed.get("selected_keys", []) if k in allowed]
        return {
            "selected_keys": keys if keys else ["puzzle", "lamp"],
            "preset": parsed.get("preset", "assembled"),
            "palette_id": parsed.get("palette_id", "warm_sun"),
            "explanation": parsed.get("explanation", "Автоматический подбор по смыслу"),
        }

    def _fallback_match(self, prompt: str) -> Dict:
        """Резервный эвристический подбор при недоступности API."""
        p = prompt.lower()
        keys = []
        if any(w in p for w in ("деньг", "фин", "крипт", "инвест", "банк", "плат")):
            keys.extend(["coin", "wallet"])
        if any(w in p for w in ("учеб", "курс", "книг", "знан", "образ")):
            keys.extend(["book", "lamp"])
        if any(w in p for w in ("техно", "it", "код", "связ", "прилож")):
            keys.extend(["phone", "puzzle"])
        if any(w in p for w in ("документ", "отчет", "договор", "проект")):
            keys.extend(["folder", "pen"])
        return {
            "selected_keys": list(dict.fromkeys(keys))[:3] or ["puzzle", "lamp"],
            "preset": "under_title" if len(prompt) > 25 else "assembled",
            "palette_id": "cool_mint" if "техно" in p else "warm_sun",
            "explanation": "Эвристический подбор по смысловым тегам",
        }

    async def analyze_metaphor(self, prompt: str) -> Dict:
        """Анализирует метафору пользователя через DeepSeek или фолбэк."""
        log.info(f"--- Анализ метафоры: '{prompt}' ---")
        if not self.settings.deepseek_api_key:
            log.warning("Ключ DeepSeek API не задан, используем эвристический фолбэк")
            return self._fallback_match(prompt)
        try:
            raw = await self._post_chat_completion(prompt)
            result = self._parse_and_validate(raw or "{}")
            log.info(f"✅ Успешный AI-анализ: {result['selected_keys']}")
            return result
        except Exception as e:
            log.error(f"⚠️ Ошибка вызова DeepSeek API: {e}. Переход на фолбэк.")
            return self._fallback_match(prompt)
