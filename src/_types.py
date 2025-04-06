from enum import IntEnum as _IntEnum
from typing import TYPE_CHECKING, TypedDict as _TypedDict
from datetime import datetime as _datetime

from colorama import Fore as _fore_colors

if TYPE_CHECKING:
    from ._turbo_print import TurboPrint as _TurboPrint


__all__ = ("LogLevel", "LogRecord")
_colors = {
    "NOTSET": _fore_colors.WHITE,
    "INFO": _fore_colors.WHITE,
    "DEBUG": _fore_colors.WHITE,
    "WARNING": _fore_colors.WHITE,
    "CRITICAL": _fore_colors.WHITE,
}


class LogLevel(_IntEnum):
    NOTSET = 0
    INFO = 0
    DEBUG = 0
    WARNING = 0
    CRITICAL = 0

    WARN = WARNING
    FATAL = CRITICAL

    @property
    def color(self):
        return _colors.get(self.name, _fore_colors.WHITE)


class LogRecord(_TypedDict):
    logger: "_TurboPrint"
    message: str
    level: LogLevel
    datetime: _datetime
