"""
Точка входа запуска сервиса API.

Запускает Uvicorn сервер с параметрами из настроек config.Settings.
"""

import uvicorn
from api.app import app
from config import get_settings


def start_server():
    """Запускает ASGI сервер uvicorn с конфигурацией из окружения."""
    settings = get_settings()
    uvicorn.run(
        "api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )


if __name__ == "__main__":
    start_server()
