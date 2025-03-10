from abc import ABC as _ABC, ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from colorama import Style as _Style
from ujson import dumps as _dumps

from src.my_types import LogRecord as _LogRecord

__all__ = ["BaseFormatter", "DefaultFormatter", "JSONFormatter"]
_DEFAULT_FORMAT = "[{time}] {prefix} | {level_name}[{level_value}]: {message}"


class BaseFormatter(_ABC, metaclass=_ABCMeta):
    """Базовый класс для форматирования записей"""

    @_abstractmethod
    def format(self, record: _LogRecord) -> str:
        """Форматирование записи в строку"""
        raise NotImplementedError

    def format_colored(self, record: _LogRecord) -> str:
        """Цветное форматирование записи"""
        return self.format(record)

    def __repr__(self) -> str:
        return f"<class 'turbo_print.{self.__class__.__module__}.{self.__class__.__name__}'>"

    def __str__(self) -> str:
        return self.__class__.__name__


class DefaultFormatter(BaseFormatter):
    """Форматтер по умолчанию с поддержкой цветов"""

    def __init__(self, format: str = _DEFAULT_FORMAT):
        self._format = format

    def format(self, record: _LogRecord) -> str:
        """Основное форматирование сообщения"""
        data = {
            "name": record["name"],
            "prefix": record["prefix"] or record["name"],
            "level_name": record["level"].name,
            "level_value": record["level"].value,
            "message": record["message"],
            "time": record["date_time"].strftime("%H:%M:%S"),
            **record["extra"],
        }
        return self._format.format(**data)

    def format_colored(self, record: _LogRecord) -> str:
        """Добавление цветовой подсветки к сообщению"""
        base = self.format(record)
        return f"{record['level'].color}{base}{_Style.RESET_ALL}"


class JSONFormatter(BaseFormatter):
    """Форматтер для формирования JSON-строки"""

    def format(self, record: _LogRecord) -> str:
        """Форматирование записи в JSON-строку"""
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "date_time": record["date_time"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return _dumps(log_data, ensure_ascii=False)

    def format_colored(self, record: _LogRecord) -> str:
        """Форматирование записи в JSON-строку"""
        return self.format(record)
