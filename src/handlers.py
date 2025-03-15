from abc import ABC, abstractmethod
from aiogram import Bot
from asyncio import Lock, get_event_loop, get_running_loop
from contextlib import suppress
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Coroutine, Literal, Optional, TextIO
import aiofiles
import aiofiles.os

from src.filters import BaseFilter
from src.formatters import BaseFormatter
from src.my_types import LogRecord

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint

try:
    _DEFAULT_ASYNC_LOOP = get_running_loop()
except RuntimeError:
    _DEFAULT_ASYNC_LOOP = get_event_loop()
__all__ = ["BaseHandler", "StreamHandler", "FileHandler", "TelegramHandler"]


class BaseHandler(ABC):
    """Базовый класс обработчиков логов."""

    def __init__(
        self,
        filters: Optional[list[BaseFilter]] = None,
        formatter: Optional[BaseFormatter] = None,
    ):
        self.filters = filters or []
        self.formatter = formatter

    @abstractmethod
    def handle(
        self,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> Coroutine[Any, Any, bool] | bool:
        """Обработка форматированной записи."""
        raise NotImplementedError


class StreamHandler(BaseHandler):
    """Вывод в консоль с поддержкой цветов."""

    def __init__(
        self,
        stream: Optional[TextIO] = None,
        use_colors: bool = True,
        filters: Optional[list[BaseFilter]] = None,
        formatter: Optional[BaseFormatter] = None,
    ) -> None:
        """
        Args:
            stream (Optional[TextIO]): Выходной поток
            use_colors (bool): Использовать цветное форматирование
        """
        self.filters = filters or []
        self.formatter = formatter
        self.stream = stream
        self.use_colors = use_colors

    def handle(
        self,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        if not all(map(lambda filter: filter.filter(record), self.filters)):
            return False
        formatted = (
            self.formatter.format_colored(record)
            if self.formatter
            else logger.formatter.format_colored(record)
        )
        if self.stream:
            self.stream.write(formatted + "\n")
            self.stream.flush()
        else:
            stdout.write(formatted + "\n")
            stdout.flush()
        return True


class TimedRotatingFileHandler(BaseHandler):
    """Обработчик для ротации файлов по времени."""

    def __init__(
        self,
        file_directory: Path,
        file_name: str = "log_{time}",
        when: Literal["S", "M", "H", "D", "midnight"] = "D",
        interval: int = 1,
        backup_count: int = 5,
        filters: Optional[list[BaseFilter]] = None,
        formatter: Optional[BaseFormatter] = None,
    ) -> None:
        """
        Args:
            file_directory (Path): Директория для хранения логов.
            file_name (str): Шаблон имени файла (поддерживает {time}).
            when (str): Интервал ротации (S - секунды, M - минуты, H - часы, D - дни, midnight - полночь).
            interval (int): Количество интервалов между ротациями.
            backup_count (int): Максимальное количество файлов для хранения.
        """
        self.filters = filters or []
        self.formatter = formatter
        self.file_directory = file_directory
        self.file_name = file_name
        self.when = when
        self.interval = interval
        self.backup_count = backup_count
        self._lock = Lock()
        self.current_file = self._get_current_file()
        self.next_rotation = self._calculate_next_rotation()

    def _calculate_next_rotation(self) -> datetime:
        """Вычисляет время следующей ротации."""
        now = datetime.now()
        if self.when == "S":
            return now + timedelta(seconds=self.interval)
        elif self.when == "M":
            return now + timedelta(minutes=self.interval)
        elif self.when == "H":
            return now + timedelta(hours=self.interval)
        elif self.when == "D" or self.when == "midnight":
            return (now + timedelta(days=self.interval)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            raise ValueError("Неподдерживаемый интервал ротации")

    def _get_current_file(self) -> Path:
        """Возвращает текущий файл для записи."""
        self.file_directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.file_name.format(time=timestamp)
        return self.file_directory / f"{filename}.log"

    async def _rotate(self) -> None:
        """Ротирует файлы логов."""
        files = sorted(
            self.file_directory.glob("*.log"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        for file in files[self.backup_count :]:
            await aiofiles.os.remove(file)

    async def handle(
        self,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        """Запись в файл с ротацией по времени."""
        if not all(map(lambda filter: filter.filter(record), self.filters)):
            return False
        async with self._lock:
            if datetime.now() >= self.next_rotation:
                self.current_file = self._get_current_file()
                self.next_rotation = self._calculate_next_rotation()
                await self._rotate()

            try:
                formatted = (
                    self.formatter.format(record)
                    if self.formatter
                    else logger.formatter.format(record)
                )
                async with aiofiles.open(self.current_file, "a", encoding="utf-8") as f:
                    await f.write(formatted + "\n")
            except OSError as e:
                stderr.write(f"OSError: Ошибка записи в файл: {str(e)}")
                stderr.flush()
                return False
        return True


class FileHandler(BaseHandler):
    """Обработчик для записи в файлы с ротацией."""

    def __init__(
        self,
        file_directory: Path,
        file_name: str = "root_{index}",
        max_size: int = 10 * 1024 * 1024,  # 10 MB
        max_lines: Optional[int] = None,
        filters: Optional[list[BaseFilter]] = None,
        formatter: Optional[BaseFormatter] = None,
    ):
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
        self.current_file = _DEFAULT_ASYNC_LOOP.run_until_complete(
            self._get_current_file()
        )
        self.filters = filters or []
        self.formatter = formatter

    async def handle(
        self,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        """Запись в файл."""
        if not all(map(lambda filter: filter.filter(record), self.filters)):
            return False
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
                formatted = (
                    self.formatter.format(record)
                    if self.formatter
                    else logger.formatter.format(record)
                )
                async with aiofiles.open(self.current_file, "a", encoding="utf-8") as f:
                    await f.write(formatted + "\n")
            except OSError as e:
                stderr.write(f"OSError: Ошибка записи в файл: {str(e)}")
                stderr.flush()
                return False
        return True

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


class BufferedFileHandler(FileHandler):
    """Обработчик с буферизацией записей."""

    def __init__(
        self,
        file_directory: Path,
        file_name: str = "root_{index}",
        max_size: int = 10 * 1024 * 1024,  # 10 MB
        max_lines: Optional[int] = None,
        buffer_size: int = 1000,
        filters: Optional[list[BaseFilter]] = None,
        formatter: Optional[BaseFormatter] = None,
    ) -> None:
        super().__init__(file_directory, file_name, max_size, max_lines)
        self.buffer_size = buffer_size
        self.buffer = []
        self.formatter = formatter
        self.filters = filters or []

    async def handle(
        self,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        """Запись в буфер с последующей записью в файл."""
        if not all(map(lambda filter: filter.filter(record), self.filters)):
            return False
        formatted = (
            self.formatter.format(record)
            if self.formatter
            else logger.formatter.format(record)
        )
        async with self._lock:
            self.buffer.append(formatted + "\n")
            if len(self.buffer) >= self.buffer_size:
                await self._flush_buffer(stderr)
        return True

    async def _flush_buffer(self, stderr) -> None:
        """Записывает буфер в файл."""
        try:
            async with aiofiles.open(self.current_file, "a", encoding="utf-8") as f:
                await f.writelines(self.buffer)
            self.buffer.clear()
        except OSError as e:
            stderr.write(f"OSError: Ошибка записи в файл: {str(e)}")
            stderr.flush()


class TelegramHandler(BaseHandler):
    """Асинхронная отправка в Telegram через бота."""

    def __init__(
        self,
        token: str,
        chat_id: int | str,
        filters: Optional[list[BaseFilter]] = None,
        formatter: Optional[BaseFormatter] = None,
    ):
        """
        Args:
            token (str): Токен бота
            chat_id (str): ID чата
        """
        self.filters = filters or []
        self.formatter = formatter
        self.bot = Bot(token)
        self.chat_id = chat_id

    async def handle(
        self,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        """Обработка записи и отправка в Telegram."""
        if not all(map(lambda filter: filter.filter(record), self.filters)):
            return False
        try:
            formatted = (
                self.formatter.format(record)
                if self.formatter
                else logger.formatter.format(record)
            )
            await self.bot.send_message(self.chat_id, formatted)
        except Exception as e:
            stderr.write(f"Ошибка отправки в Telegram: {e}" + "\n")
            stderr.flush()
            return False
        return True
