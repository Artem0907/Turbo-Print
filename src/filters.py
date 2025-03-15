from abc import ABCMeta, abstractmethod
from datetime import time
from re import compile
from typing import Protocol, runtime_checkable, Literal

from src.my_types import LogRecord, LogLevel

__all__ = ["BaseFilter", "LevelFilter", "RegexFilter", "TimeFilter"]


@runtime_checkable
class FilterProtocol(Protocol):
    def filter(self, record: "LogRecord") -> bool: ...


class BaseFilter(metaclass=ABCMeta):
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
            pattern (str): Регулярное выражение для фильтрации.
            invert (bool): Инвертировать результат фильтрации.
        """
        self.regex = compile(pattern)
        self.invert = invert

    def filter(self, record: LogRecord) -> bool:
        """Проверяет соответствие сообщения регулярному выражению.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: True, если сообщение соответствует паттерну (или не соответствует при `invert=True`).
        """
        match = bool(self.regex.search(record["message"]))
        return match if not self.invert else not match


class TimeFilter(BaseFilter):
    """Фильтрация по времени суток."""

    def __init__(self, start_time: time, end_time: time) -> None:
        """
        Args:
            start_time (time): Время начала фильтрации.
            end_time (time): Время окончания фильтрации.
        """
        self.start = start_time
        self.end = end_time

    def filter(self, record: LogRecord) -> bool:
        """Проверяет, попадает ли время записи в заданный диапазон.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: True, если время записи попадает в диапазон.
        """
        log_time = record["timestamp"].time()
        if self.start <= self.end:
            return self.start <= log_time <= self.end
        return log_time >= self.start or log_time <= self.end


class ModuleFilter(BaseFilter):
    """Фильтрация записей по имени модуля."""

    def __init__(self, module_name: str) -> None:
        self.module_name = module_name

    def filter(self, record: LogRecord) -> bool:
        return record["name"] == self.module_name


class CompositeFilter(BaseFilter):
    """Комбинирование фильтров через логические операции."""

    def __init__(
        self, filters: list[BaseFilter], mode: Literal["AND", "OR"] = "AND"
    ) -> None:
        self.filters = filters
        self.mode = mode

    def filter(self, record: LogRecord) -> bool:
        if self.mode == "AND":
            return all(f.filter(record) for f in self.filters)
        elif self.mode == "OR":
            return any(f.filter(record) for f in self.filters)
        return False
