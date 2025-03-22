import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint, LogLevel
from src.handlers import StreamHandler, FileHandler
from pathlib import Path


class LoggingAdapter:
    """Адаптер для миграции с стандартного модуля logging на TurboPrint с поддержкой асинхронности."""

    def __init__(self, logger: Optional["TurboPrint"] = None):
        """
        Args:
            logger (Optional[TurboPrint]): Логгер TurboPrint. Если None, будет создан новый.
        """
        self.logger = logger

    @staticmethod
    def convert_level(level: int) -> "LogLevel":
        """Конвертирует уровень логирования из logging в TurboPrint.

        Args:
            level (int): Уровень логирования из модуля logging.

        Returns:
            LogLevel: Соответствующий уровень логирования TurboPrint.
        """
        # level_mapping = {
        #     logging.NOTSET: LogLevel.NOTSET,
        #     logging.DEBUG: LogLevel.DEBUG,
        #     logging.INFO: LogLevel.INFO,
        #     logging.WARNING: LogLevel.WARNING,
        #     logging.ERROR: LogLevel.ERROR,
        #     logging.CRITICAL: LogLevel.CRITICAL,
        # }
        # return level_mapping.get(level, LogLevel.NOTSET)
        return level

    async def migrate_handler(self, handler: logging.Handler) -> None:
        """Асинхронная миграция обработчика из logging в TurboPrint.

        Args:
            handler (logging.Handler): Обработчик из модуля logging.
        """
        if isinstance(handler, logging.StreamHandler):
            self.logger.add_handler(StreamHandler())
        elif isinstance(handler, logging.FileHandler):
            self.logger.add_handler(FileHandler(Path(handler.baseFilename).parent))
        # Добавьте другие обработчики по необходимости

    async def migrate_logger(self, logger: logging.Logger) -> None:
        """Асинхронная миграция логгера из logging в TurboPrint.

        Args:
            logger (logging.Logger): Логгер из модуля logging.
        """
        # Уровень логирования
        self.logger.set_level(self.convert_level(logger.level))

        # Обработчики
        for handler in logger.handlers:
            await self.migrate_handler(handler)

        # Фильтры
        for filter in logger.filters:
            # Преобразуйте фильтры logging в фильтры TurboPrint
            pass

    @staticmethod
    async def auto_migrate() -> "TurboPrint":
        """Асинхронная автоматическая миграция корневого логгера logging в TurboPrint.

        Returns:
            TurboPrint: Мигрированный логгер TurboPrint.
        """
        root_logger = logging.getLogger()
        adapter = LoggingAdapter()
        await adapter.migrate_logger(root_logger)
        return adapter.logger
