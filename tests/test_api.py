"""
Тесты для проверки API эндпоинтов и бизнес-логики сервисов.
"""

import pytest
from starlette.testclient import TestClient
from api import app

client = TestClient(app)


def test_health_check():
    """Проверяет эндпоинт здоровья сервиса."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_library_list():
    """Проверяет получение списка компонентов библиотеки."""
    response = client.get("/api/v1/library")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["items"]) == data["total"]


def test_library_search():
    """Проверяет поиск компонентов по тегу 'книга'."""
    response = client.get("/api/v1/library?q=книга")
    assert response.status_code == 200
    items = response.json()["items"]
    assert any("книга" in item["tags"] or "Книга" in item["name"] for item in items)


def test_palettes_list():
    """Проверяет получение доступных цветовых схем."""
    response = client.get("/api/v1/palettes")
    assert response.status_code == 200
    palettes = response.json()["palettes"]
    assert len(palettes) >= 3


def test_manual_compose():
    """Проверяет ручную сборку композиции из переданного списка ключей."""
    payload = {
        "element_keys": ["book", "lamp", "coin"],
        "format": "1200x630",
        "preset": "assembled",
        "size": "L",
        "palette_id": "warm_sun",
    }
    response = client.post("/api/v1/compose/manual", json=payload)
    assert response.status_code == 200
    plan = response.json()["plan"]
    assert len(plan["elements"]) >= 3
    assert plan["format"] == "1200x630"


def test_ai_compose_fallback():
    """Проверяет сборку композиции по метафоре (работает как с API, так и с фолбэком)."""
    payload = {
        "prompt": "Финтех стартап и финансовая аналитика",
        "format": "1200x630",
        "size": "L",
    }
    response = client.post("/api/v1/compose/ai", json=payload)
    assert response.status_code == 200
    plan = response.json()["plan"]
    assert len(plan["elements"]) >= 2
