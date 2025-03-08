from abc import ABC as _ABC, abstractmethod as _abstractmethod
from colorama import Style as _Style

from src.types import LogRecord

__all__ = ["BaseFormatter", "DefaultFormatter"]
_DEFAULT_FORMAT = "[{time}] {prefix} | {level}: {message}"


class BaseFormatter(_ABC):
    """Базовый класс для форматирования записей"""

    @_abstractmethod
    def format(self, record: LogRecord) -> str:
        """Форматирование записи в строку"""
        pass

    def format_colored(self, record: LogRecord) -> str:
        """Цветное форматирование записи"""
        return self.format(record)

k
class DefaultFormatter(BaseFormatter):
    """Форматтер по умолчанию с поддержкой цветов"""

    def __init__(self, fmt: str = _DEFAULT_FORMAT):
        self._fmt = fmt

    def format(self, record: LogRecord) -> str:
        """Основное форматирование сообщения"""
        data = {
            "prefix": record["prefix"] if record["prefix"] else str(id(self)),
            "level": record["level"].name,
            "message": record["message"],
            "time": record["date_time"].strftime("%H:%M:%S"),
            **record["extra"],
        }
        return self._fmt.format(**data)

    def format_colored(self, record: LogRecord) -> str:
        """Добавление цветовой подсветки к сообщению"""
        base = self.format(record)
        return f"{record['level'].color}{base}{_Style.RESET_ALL}"
