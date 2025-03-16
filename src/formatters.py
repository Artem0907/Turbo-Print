from abc import ABC, abstractmethod
from io import StringIO
from colorama import Style
from yaml import dump as yaml_dump
from ujson import dumps as json_dump
from csv import DictWriter
from typing import Optional, Any, Dict, List
from string import Formatter
from datetime import datetime

from src.my_types import LogRecord
from src.localization import Localization


class BaseFormatter(ABC):
    """Базовый класс для форматирования записей логов."""

    @abstractmethod
    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка.
        """
        raise NotImplementedError

    async def format_colored(self, record: LogRecord) -> str:
        """Асинхронное цветное форматирование записи.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка с цветами.
        """
        return await self.format(record)


class DefaultFormatter(BaseFormatter):
    """Форматтер по умолчанию с поддержкой локализации и асинхронного форматирования."""

    def __init__(
        self,
        fmt: str = "[{time}] {prefix} | {level_name}[{level_value}]: {message}",
        localization: Optional[Localization] = None,
    ) -> None:
        """
        Args:
            fmt (str): Шаблон форматирования.
            localization (Optional[Localization]): Локализация.
        """
        self._fmt = fmt
        self.localization = localization or Localization()

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование сообщения.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка.
        """
        data = {
            "time": self.localization.format_datetime(record["timestamp"]),
            "name": record["name"],
            "prefix": record["prefix"] or record["name"],
            "level_name": await self.localization.translate(
                record["level"].name.lower()
            ),
            "level_value": record["level"].value,
            **record["extra"],
        }
        return self._fmt.format(**data, message=record["message"].format(**data))

    async def format_colored(self, record: LogRecord) -> str:
        """Асинхронное цветное форматирование сообщения.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка с цветами.
        """
        base = await self.format(record)
        return f"{record['level'].color}{base}{Style.RESET_ALL}"


class JSONFormatter(BaseFormatter):
    """Форматтер для формирования JSON-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в JSON-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: JSON-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return json_dump(log_data, ensure_ascii=False)


class XMLFormatter(BaseFormatter):
    """Форматтер для формирования XML-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в XML-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: XML-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return f"<log>{''.join(f'<{k}>{v}</{k}>' for k, v in log_data.items())}</log>"


class YAMLFormatter(BaseFormatter):
    """Форматтер для формирования YAML-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в YAML-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: YAML-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return yaml_dump(log_data, default_flow_style=False)


class CSVFormatter(BaseFormatter):
    """Форматтер для формирования CSV-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в CSV-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: CSV-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        output = StringIO()
        writer = DictWriter(output, fieldnames=log_data.keys())
        writer.writeheader()
        writer.writerow(log_data)
        return output.getvalue()


class HTMLFormatter(BaseFormatter):
    """Форматтер для формирования HTML-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в HTML-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: HTML-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return (
            "<div class='log-entry'>"
            + "".join(f"<p><b>{k}:</b> {v}</p>" for k, v in log_data.items())
            + "</div>"
        )


class MarkdownFormatter(BaseFormatter):
    """Форматтер для формирования Markdown-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в Markdown-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Markdown-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return "\n".join(f"**{k}:** {v}" for k, v in log_data.items())


class CustomFormatter(BaseFormatter):
    """Форматтер для создания пользовательских форматов логов."""

    def __init__(self, fmt: str, macros: Optional[Dict[str, Any]] = None) -> None:
        """
        Args:
            fmt (str): Шаблон форматирования.
            macros (Optional[Dict[str, Any]]): Пользовательские макросы.
        """
        self._fmt = fmt
        self._macros = macros or {}

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи с использованием пользовательского шаблона и макросов.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка.
        """
        formatter = Formatter()
        data = {
            "time": record["timestamp"].strftime("%H:%M:%S"),
            "name": record["name"],
            "prefix": record["prefix"] or record["name"],
            "level_name": record["level"].name,
            "level_value": record["level"].value,
            **record["extra"],
            **self._macros,  # Добавляем пользовательские макросы
        }
        return formatter.format(self._fmt, **data)
