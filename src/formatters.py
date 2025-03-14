from abc import ABC, abstractmethod
from colorama import Style
import json

from src.my_types import LogRecord

__all__ = ["BaseFormatter", "DefaultFormatter", "JSONFormatter"]


class BaseFormatter(ABC):
    """Базовый класс для форматирования записей."""

    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """Форматирование записи в строку."""
        raise NotImplementedError

    def format_colored(self, record: LogRecord) -> str:
        """Цветное форматирование записи."""
        return self.format(record)


class DefaultFormatter(BaseFormatter):
    """Форматтер по умолчанию с поддержкой цветов."""

    def __init__(
        self, fmt: str = "[{time}] {prefix} | {level_name}[{level_value}]: {message}"
    ) -> None:
        """
        Args:
            fmt (str): Шаблон форматирования
        """
        self._fmt = fmt

    def format(self, record: LogRecord) -> str:
        """Основное форматирование сообщения."""
        data = {
            "time": record["timestamp"].strftime("%H:%M:%S"),
            "prefix": record["prefix"] or record["name"],
            "level_name": record["level"].name,
            "level_value": record["level"].value,
            "message": record["message"],
            **record["extra"],
        }
        return self._fmt.format(**data)

    def format_colored(self, record: LogRecord) -> str:
        """Добавление цветовой подсветки к сообщению."""
        base = self.format(record)
        return f"{record['level'].color}{base}{Style.RESET_ALL}"


class JSONFormatter(BaseFormatter):
    """Форматтер для формирования JSON-строки."""

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в JSON-строку."""
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return json.dumps(log_data, ensure_ascii=False)
