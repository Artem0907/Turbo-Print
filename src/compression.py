import gzip
import zipfile
import rarfile
from pathlib import Path
import aiofiles
import aiofiles.os
from src.my_types import LogLevel


class Compression:
    """Класс для сжатия логов с поддержкой асинхронности."""

    def __init__(self, logger: Optional[TurboPrint] = None):
        """
        Args:
            logger (Optional[TurboPrint]): Логгер для записи ошибок.
        """
        self.logger = logger

    async def compress_gzip(self, source: Path, destination: Path) -> None:
        """Асинхронное сжатие файла в формате Gzip.

        Args:
            source (Path): Путь к исходному файлу.
            destination (Path): Путь к сжатому файлу.

        Raises:
            FileNotFoundError: Если исходный файл не найден.
            IOError: Если произошла ошибка при сжатии файла.
        """
        if not source.exists():
            error_msg = f"Файл {source} не найден"
            if self.logger:
                await self.logger(error_msg, LogLevel.ERROR)
            raise FileNotFoundError(error_msg)

        try:
            async with aiofiles.open(source, "rb") as f_in:
                async with aiofiles.open(destination, "wb") as f_out:
                    with gzip.open(f_out, "wb") as gz:
                        gz.write(await f_in.read())
            await aiofiles.os.remove(source)
        except IOError as e:
            error_msg = f"Ошибка при сжатии файла: {e}"
            if self.logger:
                await self.logger(error_msg, LogLevel.ERROR)
            raise IOError(error_msg)

    async def compress_zip(self, source: Path, destination: Path) -> None:
        """Асинхронное сжатие файла в формате Zip.

        Args:
            source (Path): Путь к исходному файлу.
            destination (Path): Путь к сжатому файлу.

        Raises:
            FileNotFoundError: Если исходный файл не найден.
            IOError: Если произошла ошибка при сжатии файла.
        """
        if not source.exists():
            error_msg = f"Файл {source} не найден"
            if self.logger:
                await self.logger(error_msg, LogLevel.ERROR)
            raise FileNotFoundError(error_msg)

        try:
            async with aiofiles.open(source, "rb") as f_in:
                with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(source, arcname=source.name)
            await aiofiles.os.remove(source)
        except IOError as e:
            error_msg = f"Ошибка при сжатии файла: {e}"
            if self.logger:
                await self.logger(error_msg, LogLevel.ERROR)
            raise IOError(error_msg)

    async def compress_rar(self, source: Path, destination: Path) -> None:
        """Асинхронное сжатие файла в формате RAR.

        Args:
            source (Path): Путь к исходному файлу.
            destination (Path): Путь к сжатому файлу.

        Raises:
            FileNotFoundError: Если исходный файл не найден.
            IOError: Если произошла ошибка при сжатии файла.
        """
        if not source.exists():
            error_msg = f"Файл {source} не найден"
            if self.logger:
                await self.logger(error_msg, LogLevel.ERROR)
            raise FileNotFoundError(error_msg)

        try:
            async with aiofiles.open(source, "rb") as f_in:
                with rarfile.RarFile(destination, "w") as rar:
                    rar.write(source, arcname=source.name)
            await aiofiles.os.remove(source)
        except IOError as e:
            error_msg = f"Ошибка при сжатии файла: {e}"
            if self.logger:
                await self.logger(error_msg, LogLevel.ERROR)
            raise IOError(error_msg)

    @staticmethod
    async def decompress_gzip(source: Path, destination: Path) -> None:
        """Асинхронная распаковка файла из формата Gzip.

        Args:
            source (Path): Путь к сжатому файлу.
            destination (Path): Путь к распакованному файлу.
        """
        async with aiofiles.open(source, "rb") as f_in:
            with gzip.open(f_in, "rb") as gz:
                async with aiofiles.open(destination, "wb") as f_out:
                    await f_out.write(gz.read())

    @staticmethod
    async def decompress_zip(source: Path, destination: Path) -> None:
        """Асинхронная распаковка файла из формата Zip.

        Args:
            source (Path): Путь к сжатому файлу.
            destination (Path): Путь к распакованному файлу.
        """
        with zipfile.ZipFile(source, "r") as zipf:
            zipf.extractall(destination)

    @staticmethod
    async def decompress_rar(source: Path, destination: Path) -> None:
        """Асинхронная распаковка файла из формата RAR.

        Args:
            source (Path): Путь к сжатому файлу.
            destination (Path): Путь к распакованному файлу.
        """
        with rarfile.RarFile(source, "r") as rar:
            rar.extractall(destination)
