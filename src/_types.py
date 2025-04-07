# Standard library imports
from datetime import datetime as _datetime
from enum import IntEnum as _IntEnum
from typing import TYPE_CHECKING
from typing import TypedDict as _TypedDict

# Third-party imports
from colorama import Fore as _ForeColors

if TYPE_CHECKING:
    from ._turbo_print import TurboPrint as _TurboPrint


__all__ = ("LogLevel", "LogRecord")

# Colors for different logging levels
_colors: dict[str, str] = {
    "NOTSET": _ForeColors.WHITE,
    "TRACE": _ForeColors.LIGHTBLUE_EX,
    "DEBUG": _ForeColors.LIGHTCYAN_EX,
    "INFO": _ForeColors.LIGHTGREEN_EX,
    "SUCCESS": _ForeColors.GREEN,
    "WARNING": _ForeColors.LIGHTYELLOW_EX,
    "FAIL": _ForeColors.RED,
    "ERROR": _ForeColors.LIGHTRED_EX,
    "CRITICAL": _ForeColors.LIGHTMAGENTA_EX,
}


class LogLevel(_IntEnum):
    """Logging levels with corresponding numeric values."""

    NOTSET = 0
    TRACE = 10
    DEBUG = 20
    INFO = 30
    SUCCESS = 40
    WARNING = 50
    FAIL = 60
    ERROR = 70
    CRITICAL = 80

    # Synonyms for compatibility
    WARN = WARNING
    FATAL = CRITICAL

    @property
    def color(self) -> str:
        """Get color for current logging level."""
        return _colors.get(self.name, _ForeColors.WHITE)


class LogRecord(_TypedDict):
    """Log record structure."""

    logger: "_TurboPrint"  # Logger that created the record
    message: str  # Message text
    level: LogLevel  # Logging level
    datetime: _datetime  # Timestamp of record creation
