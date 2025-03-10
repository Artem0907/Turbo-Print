from abc import ABC as _ABC, ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from pathlib import Path as _Path
from sys import stdout as _console
from typing import Optional as _Optional, TextIO as _TextIO
from threading import Lock as _Lock_thread
from aiogram import Bot as _Bot
from asyncio import get_running_loop as _get_running_loop, run as _async_run

from .my_types import LogRecord as _LogRecord, TurboPrintOutput as _TurboPrintOutput

__all__ = [
    "BaseHandler",
    "StreamHandler",
    "FileHandler",
    "TelegramHandler",
]
_MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10mb


class BaseHandler(_ABC, metaclass=_ABCMeta):
    """Базовый класс обработчиков логов"""

    @_abstractmethod
    def handle(self, record: _LogRecord, formatted: _TurboPrintOutput) -> None:
        """Обработка форматированной записи"""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: "{self.__class__.__module__}">'

    def __str__(self) -> str:
        return self.__class__.__name__


class StreamHandler(BaseHandler):
    """Вывод в консоль с поддержкой цветов"""

    def __init__(self, stream: _Optional[_TextIO] = None, use_colors: bool = True):
        self.stream = stream or _console
        self.use_colors = use_colors

    def handle(self, record: _LogRecord, formatted: _TurboPrintOutput) -> None:
        message = formatted[
            "colored_console" if self.use_colors else "standard_file"
        ].strip()
        self.stream.write(message + "\n")
        self.stream.flush()


class FileHandler(BaseHandler):
    """
    Args:
        file_directory (Path): Директория для хранения логов.
        file_name (str): Базовое имя файла. Default: "root".
        max_size (int): Максимальный размер файла в байтах. Default: 10 МБ.
        max_lines (Optional[int]): Максимальное количество строк в файле.
            Если None - проверка отключена. Default: None.
    """

    def __init__(
        self,
        file_directory: _Path,
        file_name: str = "root",
        max_size: int = _MAX_LOG_FILE_SIZE,
        max_lines: _Optional[int] = None,
    ):
        self.filename = file_name
        self.file_directory = file_directory
        self.max_size = max_size
        self.max_lines = max_lines
        self._lock = _Lock_thread()
        self.current_file = self._get_current_file()

    def handle(self, record: _LogRecord, formatted: _TurboPrintOutput) -> None:
        """Запись в файл"""
        with self._lock:
            if self.max_lines:
                if (
                    self.current_file.stat().st_size >= self.max_size
                    or len(
                        self.current_file.read_text("utf-8", newline="\n").split("\n")
                    )
                    >= self.max_lines
                ):
                    self.current_file = self._get_current_file()
                    self.current_file.touch()
            elif self.current_file.stat().st_size >= self.max_size:
                self.current_file = self._get_current_file()
                self.current_file.touch()

            with open(self.current_file, "a", encoding="utf-8") as f:
                f.write(formatted["standard_file"] + "\n")

    def _get_current_file(self) -> _Path:
        """Получение текущего файла"""
        self.file_directory.mkdir(parents=True, exist_ok=True)
        stamp = 0
        while True:
            candidate = self.file_directory / f"{self.filename}_{stamp}.log"
            candidate.touch()
            if self.max_lines:
                if (
                    candidate.stat().st_size < self.max_size
                    and len(candidate.read_text("utf-8", newline="\n").split("\n"))
                    < self.max_lines
                ):
                    return candidate
            elif candidate.stat().st_size < self.max_size:
                return candidate
            stamp += 1


class TelegramHandler(BaseHandler):
    """Асинхронная отправка в Telegram через бота"""

    def __init__(self, token: str, chat_id: str):
        self.bot = _Bot(token)
        self.chat_id = chat_id

    async def async_handle(
        self, record: _LogRecord, formatted: _TurboPrintOutput
    ) -> None:
        """Отправка в телеграм"""
        await self.bot.send_message(self.chat_id, formatted["standard_file"])

    def handle(self, record: _LogRecord, formatted: _TurboPrintOutput) -> None:
        try:
            loop = _get_running_loop()
            loop.create_task(self.async_handle(record, formatted))
        except RuntimeError:
            _async_run(self.async_handle(record, formatted))
