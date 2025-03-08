from abc import ABC as _ABC, abstractmethod as _abstractmethod
from re import compile as _re_compile
from datetime import time as _time

from .my_types import LogRecord as _LogRecord, LogLevel as _LogLevel

__all__ = [
    "BaseFilter",
    "LevelFilter",
    "RegexFilter",
    "TimeFilter",
]


class BaseFilter(_ABC):
    """Базовый класс для фильтрации записей лога"""

    @_abstractmethod
    def filter(self, record: _LogRecord) -> bool:
        """Фильтрация записи"""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: "{self.__class__.__module__}">'

    def __str__(self) -> str:
        return self.__class__.__name__


class LevelFilter(BaseFilter):
    """Фильтр по минимальному уровню"""

    def __init__(self, level: _LogLevel):
        self.level = level

    def filter(self, record: _LogRecord) -> bool:
        return record["level"] >= self.level


class RegexFilter(BaseFilter):
    """Фильтрация по регулярному выражению."""

    def __init__(self, pattern: str, invert: bool = False):
        self.regex = _re_compile(pattern)
        self.invert = invert

    def filter(self, record: _LogRecord) -> bool:
        match = bool(self.regex.search(record["message"]))
        return match if not self.invert else not match


class TimeFilter(BaseFilter):
    """Фильтрация по времени суток."""

    def __init__(self, start_time: _time, end_time: _time):
        self.start = start_time
        self.end = end_time

    def filter(self, record: _LogRecord) -> bool:
        log_time = record["date_time"].time()
        return self.start <= log_time <= self.end
