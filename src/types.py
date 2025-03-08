from colorama import (
    Fore as _Fore,
    Style as _Style,
)
from datetime import datetime as _datetime
from enum import Enum as _Enum
from typing import (
    Any as _Any,
    Optional as _Optional,
    TypedDict as _TypedDict,
)

__all__ = [
    "TurboPrintOutput",
    "LogLevel",
    "LogRecord",
]


class TurboPrintOutput(_TypedDict):
    """Форматы выходных данных для разных каналов"""

    colored_console: str
    standard_file: str


class LogLevel(_Enum):
    """Уровни логирования с правильным порядком приоритетов"""

    NOTSET = 0
    SUCCESS = 10
    INFO = 20
    DEBUG = 30
    LOG = 40
    WARNING = 50
    ERROR = 60
    FATAL = 70

    # Псевдонимы
    WARN = 50
    CRITICAL = 70

    @property
    def color(self) -> str:
        """Цвета для разных уровней логирования"""
        return {
            self.NOTSET: _Fore.WHITE,
            self.DEBUG: _Fore.LIGHTMAGENTA_EX,
            self.LOG: _Fore.LIGHTCYAN_EX,
            self.INFO: _Fore.BLUE,
            self.SUCCESS: _Fore.GREEN,
            self.WARNING: _Fore.LIGHTYELLOW_EX,
            self.ERROR: _Fore.LIGHTRED_EX,
            self.FATAL: _Fore.RED + _Style.BRIGHT,
        }[self]


class LogRecord(_TypedDict):
    """Структура записи лога"""

    message: str
    level: LogLevel
    prefix: _Optional[str]
    date_time: _datetime
    parent: _Optional[_Any]
    extra: dict[str, _Any]
