"""
Конфигурация приложения.

Загружает параметры окружения из .env файла через pydantic-settings.
Никакие секретные ключи или токены не хранятся в кодовой базе.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки сервиса, считываемые исключительно из переменных окружения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # deepseek_api_key — ключ доступа к DeepSeek API (строка из .env)
    deepseek_api_key: str = ""
    # deepseek_base_url — адрес шлюза API (по умолчанию https://api.deepseek.com)
    deepseek_base_url: str = "https://api.deepseek.com"
    # deepseek_model — кодовое имя модели (например deepseek-chat)
    deepseek_model: str = "deepseek-chat"

    # api_host — интерфейс привязки сервера FastAPI (например 0.0.0.0)
    api_host: str = "0.0.0.0"
    # api_port — сетевой порт сервера FastAPI
    api_port: int = 8000
    # api_debug — флаг режима отладки
    api_debug: bool = False
    # cors_origins — список разрешённых origins для CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # library_data_path — путь к JSON-индексу библиотеки компонентов
    library_data_path: str = "data/library/library.json"
    # svg_assets_dir — директория хранения SVG-файлов
    svg_assets_dir: str = "data/library/svg"


@lru_cache()
def get_settings() -> Settings:
    """
    Возвращает синглтон настроек приложения.

    Кэшируем результат через lru_cache, чтобы не перечитывать
    файл .env при каждом вызове в роутерах и сервисах.
    """
    return Settings()
