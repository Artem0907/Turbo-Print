import logging
from typing import Optional
from src.turbo_print import TurboPrint, LogLevel
from src.handlers import StreamHandler, FileHandler
from pathlib import Path


class LoggingAdapter:
    """Адаптер для миграции с стандартного модуля logging на TurboPrint."""

    def __init__(self, logger: Optional[TurboPrint] = None):
        """
        Args:
            logger (Optional[TurboPrint]): Логгер TurboPrint. Если None, будет создан новый.
        """
        self.logger = logger or TurboPrint.get_logger("migrated_logger")

    @staticmethod
    def convert_level(level: int) -> LogLevel:
        """Конвертирует уровень логирования из logging в TurboPrint."""
        level_mapping = {
            logging.NOTSET: LogLevel.NOTSET,
            logging.DEBUG: LogLevel.DEBUG,
            logging.INFO: LogLevel.INFO,
            logging.WARNING: LogLevel.WARNING,
            logging.ERROR: LogLevel.ERROR,
            logging.CRITICAL: LogLevel.CRITICAL,
        }
        return level_mapping.get(level, LogLevel.NOTSET)

    def migrate_handler(self, handler: logging.Handler) -> None:
        """Мигрирует обработчик из logging в TurboPrint."""
        if isinstance(handler, logging.StreamHandler):
            self.logger.add_handler(StreamHandler())
        elif isinstance(handler, logging.FileHandler):
            self.logger.add_handler(FileHandler(Path(handler.baseFilename).parent))
        # Добавьте другие обработчики по необходимости

    def migrate_logger(self, logger: logging.Logger) -> None:
        """Мигрирует логгер из logging в TurboPrint."""
        # Уровень логирования
        self.logger.set_level(self.convert_level(logger.level))

        # Обработчики
        for handler in logger.handlers:
            self.migrate_handler(handler)

        # Фильтры
        for filter in logger.filters:
            # Преобразуйте фильтры logging в фильтры TurboPrint
            pass

    @staticmethod
    def auto_migrate() -> TurboPrint:
        """Автоматически мигрирует корневой логгер logging в TurboPrint."""
        root_logger = logging.getLogger()
        adapter = LoggingAdapter()
        adapter.migrate_logger(root_logger)
        return adapter.logger
