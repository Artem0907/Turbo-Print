from abc import ABC, abstractmethod
from io import StringIO
from colorama import Style
from yaml import dump as yaml_dump
from ujson import dumps as json_dump
from csv import DictWriter
from typing import Optional
from string import Formatter

from src.my_types import LogRecord
from src.localization import Localization

__all__ = ["BaseFormatter", "DefaultFormatter", "JSONFormatter", "XMLFormatter", "YAMLFormatter", "CSVFormatter", "HTMLFormatter", "MarkdownFormatter"]


class BaseFormatter(ABC):
    """Базовый класс для форматирования записей."""

    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """Форматирование записи в строку."""
        raise NotImplementedError

    def format_colored(self, record: LogRecord) -> str:
        """Цветное форматирование записи."""
        return self.format(record)


class DefaultFormatter(BaseFormatter):
    """Форматтер по умолчанию с поддержкой локализации."""

    def __init__(self, fmt: str = "[{time}] {prefix} | {level_name}[{level_value}]: {message}", localization: Optional[Localization] = None) -> None:
        """
        Args:
            fmt (str): Шаблон форматирования.
            localization (Optional[Localization]): Локализация.
        """
        self._fmt = fmt
        self.localization = localization or Localization()

    def format(self, record: LogRecord) -> str:
        """Основное форматирование сообщения."""
        data = {
            "time": self.localization.format_datetime(record["timestamp"]),
            "name": record["name"],
            "prefix": record["prefix"] or record["name"],
            "level_name": self.localization.translate(record["level"].name.lower()),
            "level_value": record["level"].value,
            **record["extra"],
        }
        return self._fmt.format(**data, message=record["message"].format(**data))

    def format_colored(self, record: LogRecord) -> str:
        """Добавление цветовой подсветки к сообщению."""
        base = self.format(record)
        return f"{record['level'].color}{base}{Style.RESET_ALL}"


class JSONFormatter(BaseFormatter):
    """Форматтер для формирования JSON-строки."""

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в JSON-строку."""
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

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в XML-строку."""
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

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в YAML-строку."""
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

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в CSV-строку."""
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

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в HTML-строку."""
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

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в Markdown-строку."""
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

    def format(self, record: LogRecord) -> str:
        """Форматирование записи с использованием пользовательского шаблона и макросов."""
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