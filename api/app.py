"""
Инициализация и конфигурация FastAPI приложения.

Создаёт приложение, подключает CORS middleware, роутеры и статическую раздачу SVG.
"""

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.router.compose import router as compose_router
from api.router.library import router as library_router
from api.router.palette import router as palette_router
from config import get_settings
from core.logger import get_logger

log = get_logger("api_app")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом: логирование запуска и завершения."""
    log.info("=" * 60)
    log.info("ЗАПУСК Сервиса генерации векторных композиций")
    log.info(f"  Хост: {settings.api_host}:{settings.api_port}")
    log.info(f"  Отладка: {settings.api_debug}")
    log.info("=" * 60)
    yield
    log.info("ОСТАНОВКА Сервиса генерации векторных композиций")


def _mount_static_dirs(app: FastAPI):
    """Монтирует каталоги SVG библиотеки и фронтенда при наличии сборки."""
    svg_dir = os.path.join(os.getcwd(), "data", "library", "svg")
    os.makedirs(svg_dir, exist_ok=True)
    app.mount("/library/svg", StaticFiles(directory=svg_dir), name="svg_static")
    dist_dir = os.path.join(os.getcwd(), "frontend", "dist")
    if os.path.exists(dist_dir):
        app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")


def create_app() -> FastAPI:
    """Создаёт и конфигурирует экземпляр FastAPI приложения."""
    app = FastAPI(
        title="Vector Illustration Composer API",
        version="1.0.0",
        description="Сервис сборки векторных композиций из компонентов Figma",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(library_router)
    app.include_router(compose_router)
    app.include_router(palette_router)

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "vector_composer"}

    _mount_static_dirs(app)
    return app


app = create_app()
