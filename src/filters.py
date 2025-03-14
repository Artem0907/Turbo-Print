from abc import ABC, abstractmethod
from datetime import time
from re import compile

from src.my_types import LogRecord, LogLevel

__all__ = ["BaseFilter", "LevelFilter", "RegexFilter", "TimeFilter"]


class BaseFilter(ABC):
    """Базовый класс для фильтрации логов."""
    
    @abstractmethod
    def filter(self, record: LogRecord) -> bool:
        """Фильтрация записи лога.

        Args:
            record (LogRecord): Запись для фильтрации

        Returns:
            bool: True если запись должна быть обработана
        """
        raise NotImplementedError


class LevelFilter(BaseFilter):
    """Фильтр по минимальному уровню логирования."""
    
    def __init__(self, level: LogLevel) -> None:
        """
        Args:
            level (LogLevel): Минимальный уровень для фильтрации
        """
        self.level = level

    def filter(self, record: LogRecord) -> bool:
        """Применить фильтр по уровню логирования.
        
        Returns:
            bool: True если уровень записи >= установленного уровня
        """
        return record["level"] >= self.level


class RegexFilter(BaseFilter):
    """Фильтрация по регулярному выражению."""

    def __init__(self, pattern: str, invert: bool = False) -> None:
        """
        Args:
            pattern (str): Регулярное выражение для фильтрации
            invert (bool): Инвертировать результат фильтрации
        """
        self.regex = compile(pattern)
        self.invert = invert

    def filter(self, record: LogRecord) -> bool:
        match = bool(self.regex.search(record["message"]))
        return match if not self.invert else not match


class TimeFilter(BaseFilter):
    """Фильтрация по времени суток."""

    def __init__(self, start_time: time, end_time: time) -> None:
        """
        Args:
            start_time (time): Время начала фильтрации
            end_time (time): Время окончания фильтрации
        """
        self.start = start_time
        self.end = end_time

    def filter(self, record: LogRecord) -> bool:
        log_time = record["timestamp"].time()
        if self.start <= self.end:
            return self.start <= log_time <= self.end
        return log_time >= self.start or log_time <= self.end
