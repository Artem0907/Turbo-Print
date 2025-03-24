from colorama import Fore, Style
from datetime import datetime
from enum import IntEnum
from typing import Optional, TypedDict, TYPE_CHECKING, Any
from functools import cached_property
from ujson import load as json_load
from pathlib import Path
from yaml import safe_load as yaml_safe_load

if TYPE_CHECKING:
    from .turbo_print import TurboPrint


class TurboPrintOutput(TypedDict):
    """Форматы выходных данных для разных каналов.

    Attributes:
        colored_console (str): Форматированная строка с цветами для консоли.
        standard_file (str): Стандартная строка для записи в файл.
    """

    colored_console: str
    standard_file: str


class LogLevel(IntEnum):
    """Уровни логирования с цветовым оформлением."""

    NOTSET = 0
    TRACE = 5
    DEBUG = 10
    INFO = 20
    NOTICE = 25
    SUCCESS = 30
    WARNING = 40
    ERROR = 50
    CRITICAL = 60
    SECURITY = 70

    @classmethod
    def add_custom_level(cls, name: str, value: int, color: str) -> "LogLevel":
        """
        Добавляет кастомный уровень логирования.

        Args:
            name (str): Имя уровня.
            value (int): Значение уровня.
            color (str): Цвет для отображения в консоли.

        Returns:
            LogLevel: Новый уровень логирования.
        """
        if name in cls._member_names_:
            raise ValueError(f"Уровень {name} уже существует")

        new_level = IntEnum(name, {name: value}, type=cls)
        new_level.color = color  # type: ignore
        return new_level  # type: ignore

    @cached_property
    def color(self) -> str:
        """Цветовое представление уровня для консоли.

        Returns:
            str: Цвет уровня.
        """
        colors = {
            LogLevel.NOTSET: Fore.WHITE,
            LogLevel.TRACE: Fore.CYAN + Style.DIM,
            LogLevel.DEBUG: Fore.CYAN,
            LogLevel.INFO: Fore.BLUE,
            LogLevel.NOTICE: Fore.GREEN + Style.BRIGHT,
            LogLevel.SUCCESS: Fore.GREEN,
            LogLevel.WARNING: Fore.YELLOW,
            LogLevel.ERROR: Fore.RED,
            LogLevel.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
            LogLevel.SECURITY: Fore.RED + Style.BRIGHT,
        }
        return colors[self]


class LogRecord(TypedDict):
    """Структура записи лога.

    Attributes:
        message (str): Сообщение лога.
        level (LogLevel): Уровень логирования.
        name (str): Имя логгера.
        prefix (Optional[str]): Префикс лога.
        timestamp (datetime): Временная метка.
        parent (Optional["TurboPrint"]): Родительский логгер.
        extra (dict[str, Any]): Дополнительные данные.
        tags (list[str]): Теги.
        category (Optional[str]): Категория.
    """

    message: str
    level: LogLevel
    name: str
    prefix: Optional[str]
    timestamp: datetime
    parent: Optional["TurboPrint"]
    extra: dict[str, Any]
    tags: list[str]
    category: Optional[str]


class TurboPrintConfig:
    """Класс для загрузки конфигурации логгера."""

    @staticmethod
    def from_json(file_path: Path) -> dict[str, Any]:
        """Загружает конфигурацию из JSON файла.

        Args:
            file_path (Path): Путь к JSON файлу.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json_load(f)

    @staticmethod
    def from_yaml(file_path: Path) -> dict[str, Any]:
        """Загружает конфигурацию из YAML файла.

        Args:
            file_path (Path): Путь к YAML файлу.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml_safe_load(f)

    @staticmethod
    def configure_from_file(file_path: Path) -> "TurboPrint":
        """Создаёт логгер на основе конфигурации из файла.

        Args:
            file_path (Path): Путь к файлу конфигурации.

        Returns:
            TurboPrint: Настроенный логгер.
        """
        if file_path.suffix == ".json":
            config = TurboPrintConfig.from_json(file_path)
        elif file_path.suffix in (".yaml", ".yml"):
            config = TurboPrintConfig.from_yaml(file_path)
        else:
            raise ValueError("Неподдерживаемый формат файла")

        return TurboPrint(**config)
