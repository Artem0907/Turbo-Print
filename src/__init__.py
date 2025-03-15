"""
TurboPrint - мощная и гибкая система логирования для Python.

Основные возможности:
- Иерархические логгеры с поддержкой наследования настроек.
- Поддержка цветного вывода в консоль.
- Ротация лог-файлов по размеру.
- Асинхронная отправка логов в Telegram.
- Гибкая система фильтрации и форматирования.

Пример использования:

    from turbo_print import TurboPrint, LogLevel
    from turbo_print.handlers import StreamHandler, FileHandler
    from pathlib import Path

    # Создание логгера
    logger = TurboPrint.get_logger("app")
    logger.add_handler(StreamHandler())
    logger.add_handler(FileHandler(Path("logs"), "app"))

    # Логирование
    logger("Запуск приложения", LogLevel.INFO)
    logger("Ошибка подключения к базе данных", LogLevel.ERROR)

Для более сложных сценариев используйте иерархию логгеров:

    parent_logger = TurboPrint.get_logger("parent")
    child_logger = TurboPrint.get_logger("parent.child")

    parent_logger("Сообщение от родителя", LogLevel.INFO)
    child_logger("Сообщение от дочернего логгера", LogLevel.DEBUG)
"""

from . import (
    filters,
    formatters,
    handlers,
    my_types,
    turbo_print,
    inner_middlewares,
    outer_middlewares,
)

__all__ = [
    "filters",
    "formatters",
    "handlers",
    "my_types",
    "turbo_print",
    "inner_middlewares",
    "outer_middlewares",
]
