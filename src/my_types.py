# type: ignore
from colorama import (
    Fore as _Fore,
    Style as _Style,
)
from datetime import datetime as _datetime
from enum import Enum as _Enum
from typing import (
    Any as _Any,
    Optional as _Optional,
    Self as _Self,
    TypedDict as _TypedDict,
)

__all__ = [
    "TurboPrintOutput",
    _Self,
    "LogRecord",
]


class TurboPrintOutput(_TypedDict):
    """Форматы выходных данных для разных каналов"""

    colored_console: str
    standard_file: str


class LogLevel(_Enum):
    """Уровни логирования с правильным порядком приоритетов"""

    NOTSET = 0
    DEBUG = 10
    INFO = 20
    SUCCESS = 30
    LOG = 40
    WARNING = 50
    ERROR = 60
    FATAL = 70

    # Псевдонимы
    WARN = WARNING
    CRITICAL = FATAL

    @property
    def color(self) -> str:
        """Цвета для разных уровней логирования"""
        return {
            0: _Fore.WHITE,
            10: _Fore.LIGHTMAGENTA_EX,
            20: _Fore.BLUE,
            30: _Fore.GREEN,
            40: _Fore.LIGHTCYAN_EX,
            50: _Fore.LIGHTYELLOW_EX,
            60: _Fore.LIGHTRED_EX,
            70: _Fore.RED + _Style.BRIGHT,
        }[self.value]

    def __eq__(self, other: _Self | int) -> bool:
        """Определяет поведение оператора равенства, =="""
        return (
            self.value == other.value
            if isinstance(other, LogLevel)
            else self.value == other
        )

    def __ne__(self, other: _Self | int) -> bool:
        """Определяет поведение оператора неравенства, !="""
        return (
            self.value != other.value
            if isinstance(other, LogLevel)
            else self.value != other
        )

    def __lt__(self, other: _Self | int) -> bool:
        """Определяет поведение оператора меньше, <"""
        return (
            self.value < other.value
            if isinstance(other, LogLevel)
            else self.value < other
        )

    def __gt__(self, other: _Self | int) -> bool:
        """Определяет поведение оператора больше, >"""
        return (
            self.value > other.value
            if isinstance(other, LogLevel)
            else self.value > other
        )

    def __le__(self, other: _Self | int) -> bool:
        """Определяет поведение оператора меньше или равно, <="""
        return (
            self.value <= other.value
            if isinstance(other, LogLevel)
            else self.value <= other
        )

    def __ge__(self, other: _Self | int) -> bool:
        """Определяет поведение оператора больше или равно, >="""
        return (
            self.value >= other.value
            if isinstance(other, LogLevel)
            else self.value >= other
        )

    def __invert__(self) -> _Self:
        """Определяет поведение для инвертирования оператором ~"""
        return self

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__}[{self.name}]: "{self.__class__.__module__}">'
        )

    def __str__(self) -> str:
        return self.name


class LogRecord(_TypedDict):
    """Структура записи лога"""

    message: str
    name: str
    level: LogLevel
    prefix: _Optional[str]
    date_time: _datetime
    parent: _Optional["TurboPrint"]
    extra: dict[str, _Any]
