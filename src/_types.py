from enum import IntEnum as _IntEnum
from typing import TYPE_CHECKING, TypedDict as _TypedDict
from datetime import datetime as _datetime

from colorama import Fore as _fore_colors

if TYPE_CHECKING:
    from ._turbo_print import TurboPrint as _TurboPrint


__all__ = ("LogLevel", "LogRecord")
_colors: dict[str, str] = {
    "NOTSET": _fore_colors.WHITE,
    "INFO": _fore_colors.WHITE,
    "DEBUG": _fore_colors.WHITE,
    "WARNING": _fore_colors.WHITE,
    "CRITICAL": _fore_colors.WHITE,
    "ERROR": _fore_colors.WHITE,
    "TRACE": _fore_colors.WHITE,
}


class LogLevel(_IntEnum):
    NOTSET = 0
    INFO = 1
    DEBUG = 2
    WARNING = 3
    CRITICAL = 4
    ERROR = 5
    TRACE = 6

    WARN = WARNING
    FATAL = CRITICAL

    @property
    def color(self) -> str:
        return _colors.get(self.name, _fore_colors.WHITE)


class LogRecord(_TypedDict):
    logger: "_TurboPrint"
    message: str
    level: LogLevel
    datetime: _datetime
