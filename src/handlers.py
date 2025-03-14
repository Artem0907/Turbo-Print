from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from sys import stdout
from typing import Optional, TextIO
from threading import Lock
from aiogram import Bot
from asyncio import get_running_loop, run_coroutine_threadsafe

from src.my_types import LogRecord, TurboPrintOutput

__all__ = ["BaseHandler", "StreamHandler", "FileHandler", "TelegramHandler"]


class BaseHandler(ABC):
    """Базовый класс обработчиков логов."""

    @abstractmethod
    def handle(self, record: LogRecord, formatted: TurboPrintOutput) -> None:
        """Обработка форматированной записи."""
        raise NotImplementedError


class StreamHandler(BaseHandler):
    """Вывод в консоль с поддержкой цветов."""

    def __init__(
        self, stream: Optional[TextIO] = None, use_colors: bool = True
    ) -> None:
        """
        Args:
            stream (Optional[TextIO]): Выходной поток
            use_colors (bool): Использовать цветное форматирование
        """
        self.stream = stream or stdout
        self.use_colors = use_colors

    def handle(self, record: LogRecord, formatted: TurboPrintOutput) -> None:
        message = formatted[
            "colored_console" if self.use_colors else "standard_file"
        ].strip()
        self.stream.write(message + "\n")
        self.stream.flush()


class FileHandler(BaseHandler):
    """Обработчик для записи в файлы с ротацией."""

    def __init__(
        self,
        file_directory: Path,
        file_name: str = "root_{index}",
        max_size: int = 10 * 1024 * 1024,  # 10 MB
        max_lines: Optional[int] = None,
    ) -> None:
        """
        Args:
            file_directory (Path): Директория для хранения логов
            file_name (str): Базовое имя файла (с форматом, поддерживает: date, time, `index`)
            max_size (int): Максимальный размер файла в байтах
            max_lines (Optional[int]): Максимальное количество строк
        """
        if "{index}" not in file_name:
            raise ValueError("no `index` format")
        self.filename = file_name
        self.file_directory = file_directory
        self.max_size = max_size
        self.max_lines = max_lines
        self._lock = Lock()
        self.current_file = self._get_current_file()

    def handle(self, record: LogRecord, formatted: TurboPrintOutput) -> None:
        """Запись в файл."""
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

            try:
                with open(self.current_file, "a", encoding="utf-8") as f:
                    f.write(formatted["standard_file"] + "\n")
            except OSError as e:
                print(f"Ошибка записи в файл: {e}")

    def _get_current_file(self) -> Path:
        """Получение текущего файла."""
        self.file_directory.mkdir(parents=True, exist_ok=True)
        stamp = 1
        while True:
            filename = self.filename.format(
                date=datetime.now().strftime("%d/%m/%Y"),
                time=datetime.now().strftime("%H:%M"),
                index=stamp,
            )
            candidate = self.file_directory / f"{filename}.log"
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
    """Асинхронная отправка в Telegram через бота."""

    def __init__(self, token: str, chat_id: str) -> None:
        """
        Args:
            token (str): Токен бота
            chat_id (str): ID чата
        """
        self.bot = Bot(token)
        self.chat_id = chat_id

    async def async_handle(
        self, record: LogRecord, formatted: TurboPrintOutput
    ) -> None:
        """Отправка в Telegram."""
        await self.bot.send_message(self.chat_id, formatted["standard_file"])

    def handle(self, record: LogRecord, formatted: TurboPrintOutput) -> None:
        """Обработка записи."""
        try:
            loop = get_running_loop()
            loop.create_task(self.async_handle(record, formatted))
        except RuntimeError:
            run_coroutine_threadsafe(
                self.async_handle(record, formatted), get_running_loop()
            )
