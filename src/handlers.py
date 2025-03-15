from abc import ABC, abstractmethod
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Any, Coroutine, Optional, TextIO
from asyncio import Lock, get_event_loop
from aiogram import Bot
import aiofiles
import aiofiles.os

from src.my_types import LogRecord, TurboPrintOutput

__all__ = ["BaseHandler", "StreamHandler", "FileHandler", "TelegramHandler"]


class BaseHandler(ABC):
    """Базовый класс обработчиков логов."""

    @abstractmethod
    def handle(
        self,
        record: LogRecord,
        formatted: TurboPrintOutput,
        stdout: TextIO,
        stderr: TextIO,
    ) -> Coroutine[Any, Any, None] | None:
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
        self.stream = stream
        self.use_colors = use_colors

    def handle(
        self,
        record: LogRecord,
        formatted: TurboPrintOutput,
        stdout: TextIO,
        stderr: TextIO,
    ) -> None:
        message = formatted[
            "colored_console" if self.use_colors else "standard_file"
        ].strip()
        if self.stream:
            self.stream.write(message + "\n")
            self.stream.flush()
        else:
            stdout.write(message + "\n")
            stdout.flush()


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
        self.current_file = get_event_loop().run_until_complete(
            self._get_current_file()
        )

    async def handle(
        self,
        record: LogRecord,
        formatted: TurboPrintOutput,
        stdout: TextIO,
        stderr: TextIO,
    ) -> None:
        """Запись в файл."""
        async with self._lock:
            if self.max_lines:
                if (
                    self.current_file.stat().st_size >= self.max_size
                    or len(
                        self.current_file.read_text("utf-8", newline="\n").split("\n")
                    )
                    >= self.max_lines
                ):

                    self.current_file = await self._get_current_file()
                    self.current_file.touch()

            try:
                async with aiofiles.open(self.current_file, "a", encoding="utf-8") as f:
                    await f.write(formatted["standard_file"] + "\n")
            except OSError as e:
                stderr.write(f"OSError: Ошибка записи в файл: {str(e)}")
                stderr.flush()

    async def _get_current_file(self) -> Path:
        """Асинхронное получение текущего файла."""
        self.file_directory.mkdir(parents=True, exist_ok=True)
        stamp = 1
        while True:
            filename = self.filename.format(
                date=datetime.now().strftime("%d/%m/%Y"),
                time=datetime.now().strftime("%H:%M"),
                index=stamp,
            )
            candidate = self.file_directory / f"{filename}.log"
            if await aiofiles.os.path.exists(candidate):
                stamp += 1
                continue
            with suppress(FileExistsError):
                await aiofiles.os.mkdir(self.file_directory)
            with suppress(FileExistsError):
                await (await aiofiles.open(candidate, "x", encoding="utf-8")).close()
            if self.max_lines:
                file_size = (await aiofiles.os.stat(candidate)).st_size
                async with aiofiles.open(candidate, "r", encoding="utf-8") as f:
                    lines = sum(1 for _ in await f.readlines())
                if file_size < self.max_size and lines < self.max_lines:
                    return candidate
            else:
                if (await aiofiles.os.stat(candidate)).st_size < self.max_size:
                    return candidate
            stamp += 1


class TelegramHandler(BaseHandler):
    """Асинхронная отправка в Telegram через бота."""

    def __init__(self, token: str, chat_id: int | str) -> None:
        """
        Args:
            token (str): Токен бота
            chat_id (str): ID чата
        """
        self.bot = Bot(token)
        self.chat_id = chat_id

    async def handle(
        self,
        record: LogRecord,
        formatted: TurboPrintOutput,
        stdout: TextIO,
        stderr: TextIO,
    ) -> None:
        """Обработка записи и отправка в Telegram"""
        await self.bot.send_message(self.chat_id, formatted["standard_file"])
