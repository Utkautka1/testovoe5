"""
Модуль централизованного логирования приложения.

Предоставляет фабрику логгеров с единообразным форматированием
для терминала и файлового вывода при необходимости.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Создаёт или возвращает сконфигурированный логгер по смысловому имени.

    Используем смысловые имена подсистем вместо имен файлов,
    чтобы легко фильтровать логирование модулей в продакшене.
    Возвращает экземпляр logging.Logger.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
