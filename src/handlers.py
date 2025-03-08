from abc import ABC as _ABC, abstractmethod as _abstractmethod
from pathlib import Path as _Path
from sys import stdout as _console
from typing import Optional as _Optional, TextIO as _TextIO
from threading import Lock as _Lock_thread
from aiogram import Bot as _Bot
from asyncio import get_event_loop as _get_event_loop

from src.types import LogRecord as _LogRecord, TurboPrintOutput as _TurboPrintOutput

__all__ = [
    "BaseHandler",
    "StreamHandler",
    "FileHandler",
    "TelegramHandler",
]
_MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10mb


class BaseHandler(_ABC):
    """Базовый класс обработчиков логов"""

    @_abstractmethod
    def handle(self, record: _LogRecord, formatted: _TurboPrintOutput) -> None:
        """Обработка форматированной записи"""
        pass

    def close(self) -> None:
        """Завершение работы обработчика"""
        pass

    def flush(self) -> None:
        """Сброс буферов"""
        pass


class StreamHandler(BaseHandler):
    """Обработчик для вывода в стандартные потоки (консоль)"""

    def __init__(self, stream: _Optional[_TextIO] = None, use_colors: bool = True):
        self.stream = stream or _console
        self.use_colors = use_colors

    def handle(self, record: _LogRecord, formatted: _TurboPrintOutput) -> None:
        """Запись в поток вывода"""
        message = formatted["colored_console" if self.use_colors else "standard_file"]
        self.stream.write(message + "\n")
        self.flush()

    def flush(self) -> None:
        """Сброс буфера потока"""
        if self.stream and not self.stream.closed:
            self.stream.flush()


class FileHandler(BaseHandler):
    """Обработчик для записи в файлы с ротацией по размеру"""

    def __init__(
        self,
        file_path: _Path,
        file_name: _Optional[str] = None,
        max_size: int = _MAX_LOG_FILE_SIZE,
    ):
        self.stamp = 0
        self.file_path = file_path
        self.file_rotate_name = (
            f"{file_name}_{self.stamp}.log" if file_name else f"{self.stamp}.log"
        )
        self.filename = file_name
        self.max_size = max_size
        self._lock = _Lock_thread()
        file_path.mkdir(parents=True, exist_ok=True)

    def handle(self, record: _LogRecord, formatted: _TurboPrintOutput) -> None:
        """Запись в файл с проверкой ротации"""
        with self._lock:
            self._rotate()
            with open(
                self.file_path.joinpath(self.file_rotate_name), "a+", encoding="utf-8"
            ) as f:
                f.write(formatted["standard_file"] + "\n")

    def _rotate(self) -> None:
        """Ротация файлов при превышении максимального размера"""

        if self.file_path.joinpath(self.file_rotate_name).exists():
            if (
                self.file_path.joinpath(self.file_rotate_name).stat().st_size
                >= self.max_size
            ):
                self.stamp += 1
                self.file_rotate_name = (
                    f"{self.filename}_{self.stamp}.log"
                    if self.filename
                    else f"{self.stamp}.log"
                )


class TelegramHandler(BaseHandler):
    """Обработчик для отправки в телеграм"""

    def __init__(self, token: str, chat_id: str):
        self.bot = _Bot(token)
        self.async_loop = _get_event_loop().run_until_complete
        self.chat_id = chat_id

    def handle(self, record: _LogRecord, formatted: _TurboPrintOutput) -> None:
        """Отправка в телеграм"""
        self.async_loop(self.bot.send_message(self.chat_id, formatted["standard_file"]))
