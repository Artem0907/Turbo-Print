from colorama import Fore, Style
from datetime import datetime
from enum import IntEnum
from typing import Optional, TypedDict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint

__all__ = ["TurboPrintOutput", "LogLevel", "LogRecord"]


class TurboPrintOutput(TypedDict):
    """Форматы выходных данных для разных каналов.

    Attributes:
        colored_console (str): Форматированная строка с цветами для консоли
        standard_file (str): Стандартная строка для записи в файл
    """

    colored_console: str
    standard_file: str


class LogLevel(IntEnum):
    """Уровни логирования с цветовым оформлением."""

    NOTSET = 0
    DEBUG = 10
    INFO = 20
    SUCCESS = 30
    WARNING = 40
    ERROR = 50
    CRITICAL = 60

    @property
    def color(self) -> str:
        """Цветовое представление уровня для консоли."""
        colors = {
            LogLevel.NOTSET: Fore.WHITE,
            LogLevel.DEBUG: Fore.CYAN,
            LogLevel.INFO: Fore.BLUE,
            LogLevel.SUCCESS: Fore.GREEN,
            LogLevel.WARNING: Fore.YELLOW,
            LogLevel.ERROR: Fore.RED,
            LogLevel.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
        }
        return colors[self]


class LogRecord(TypedDict):
    """Структура записи лога."""

    message: str
    level: LogLevel
    name: str
    prefix: Optional[str]
    timestamp: datetime
    parent: Optional["TurboPrint"]  # Используем аннотацию
    extra: dict[str, Any]
