import gzip
import zipfile
import rarfile
import py7zr
import tarfile
from pathlib import Path
import aiofiles
import aiofiles.os
from typing import Optional, TYPE_CHECKING
from src.my_types import LogLevel

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint

__all__ = ["Compression"]


class Compression:
    """Класс для сжатия и распаковки файлов с поддержкой асинхронности."""

    def __init__(self, logger: Optional["TurboPrint"] = None):
        """
        Args:
            logger (Optional[TurboPrint]): Логгер для записи ошибок.
        """
        self.logger = logger

    async def compress_gzip(
        self, source: Path, destination: Path, compression_level: int = 9
    ) -> None:
        """Асинхронное сжатие файла в формате Gzip.

        Args:
            source (Path): Путь к исходному файлу.
            destination (Path): Путь к сжатому файлу.
            compression_level (int): Уровень сжатия (от 0 до 9).

        Raises:
            FileNotFoundError: Если исходный файл не найден.
            IOError: Если произошла ошибка при сжатии файла.
        """
        if not source.exists():
            error_msg = f"Файл {source} не найден"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise FileNotFoundError(error_msg)

        try:
            async with aiofiles.open(source, "rb") as f_in:
                async with aiofiles.open(destination, "wb") as f_out:
                    with gzip.GzipFile(
                        fileobj=f_out, mode="wb", compresslevel=compression_level
                    ) as gz:
                        gz.write(await f_in.read())
            await aiofiles.os.remove(source)
            if self.logger:
                self.logger(
                    f"Файл {source} успешно сжат в {destination}", LogLevel.INFO
                )
        except IOError as e:
            error_msg = f"Ошибка при сжатии файла: {e}"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise IOError(error_msg)

    async def compress_zip(
        self, source: Path, destination: Path, compression_level: int = 9
    ) -> None:
        """Асинхронное сжатие файла в формате Zip.

        Args:
            source (Path): Путь к исходному файлу.
            destination (Path): Путь к сжатому файлу.
            compression_level (int): Уровень сжатия (от 0 до 9).

        Raises:
            FileNotFoundError: Если исходный файл не найден.
            IOError: Если произошла ошибка при сжатии файла.
        """
        if not source.exists():
            error_msg = f"Файл {source} не найден"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise FileNotFoundError(error_msg)

        try:
            async with aiofiles.open(source, "rb") as f_in:
                with zipfile.ZipFile(
                    destination,
                    "w",
                    zipfile.ZIP_DEFLATED,
                    compresslevel=compression_level,
                ) as zipf:
                    zipf.write(source, arcname=source.name)
            await aiofiles.os.remove(source)
            if self.logger:
                self.logger(
                    f"Файл {source} успешно сжат в {destination}", LogLevel.INFO
                )
        except IOError as e:
            error_msg = f"Ошибка при сжатии файла: {e}"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise IOError(error_msg)

    async def compress_rar(
        self, source: Path, destination: Path, compression_level: int = 5
    ) -> None:
        """Асинхронное сжатие файла в формате RAR.

        Args:
            source (Path): Путь к исходному файлу.
            destination (Path): Путь к сжатому файлу.
            compression_level (int): Уровень сжатия (от 0 до 5).

        Raises:
            FileNotFoundError: Если исходный файл не найден.
            IOError: Если произошла ошибка при сжатии файла.
        """
        if not source.exists():
            error_msg = f"Файл {source} не найден"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise FileNotFoundError(error_msg)

        try:
            async with aiofiles.open(source, "rb") as f_in:
                with rarfile.RarFile(
                    destination, "w", compression_level=compression_level
                ) as rar:
                    rar.write(source, arcname=source.name)
            await aiofiles.os.remove(source)
            if self.logger:
                self.logger(
                    f"Файл {source} успешно сжат в {destination}", LogLevel.INFO
                )
        except IOError as e:
            error_msg = f"Ошибка при сжатии файла: {e}"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise IOError(error_msg)

    async def compress_7z(
        self, source: Path, destination: Path, compression_level: int = 5
    ) -> None:
        """Асинхронное сжатие файла в формате 7z.

        Args:
            source (Path): Путь к исходному файлу.
            destination (Path): Путь к сжатому файлу.
            compression_level (int): Уровень сжатия (от 0 до 9).

        Raises:
            FileNotFoundError: Если исходный файл не найден.
            IOError: Если произошла ошибка при сжатии файла.
        """
        if not source.exists():
            error_msg = f"Файл {source} не найден"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise FileNotFoundError(error_msg)

        try:
            async with aiofiles.open(source, "rb") as f_in:
                with py7zr.SevenZipFile(
                    destination, "w", compression_level=compression_level
                ) as archive:
                    archive.write(source, arcname=source.name)
            await aiofiles.os.remove(source)
            if self.logger:
                self.logger(
                    f"Файл {source} успешно сжат в {destination}", LogLevel.INFO
                )
        except IOError as e:
            error_msg = f"Ошибка при сжатии файла: {e}"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise IOError(error_msg)

    async def compress_tar(
        self, source: Path, destination: Path, compression: Optional[str] = None
    ) -> None:
        """Асинхронное сжатие файла в формате Tar.

        Args:
            source (Path): Путь к исходному файлу.
            destination (Path): Путь к сжатому файлу.
            compression (Optional[str]): Тип сжатия (gz, bz2, xz).

        Raises:
            FileNotFoundError: Если исходный файл не найден.
            IOError: Если произошла ошибка при сжатии файла.
        """
        if not source.exists():
            error_msg = f"Файл {source} не найден"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise FileNotFoundError(error_msg)

        try:
            async with aiofiles.open(source, "rb") as f_in:
                mode = "w"
                if compression:
                    mode += f":{compression}"
                with tarfile.open(destination, mode) as tar:
                    tar.add(source, arcname=source.name)
            await aiofiles.os.remove(source)
            if self.logger:
                self.logger(
                    f"Файл {source} успешно сжат в {destination}", LogLevel.INFO
                )
        except IOError as e:
            error_msg = f"Ошибка при сжатии файла: {e}"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
            raise IOError(error_msg)

    @staticmethod
    async def decompress_gzip(source: Path, destination: Path) -> None:
        """Асинхронная распаковка файла из формата Gzip.

        Args:
            source (Path): Путь к сжатому файлу.
            destination (Path): Путь к распакованному файлу.

        Raises:
            FileNotFoundError: Если сжатый файл не найден.
            IOError: Если произошла ошибка при распаковке файла.
        """
        if not source.exists():
            raise FileNotFoundError(f"Файл {source} не найден")

        try:
            async with aiofiles.open(source, "rb") as f_in:
                with gzip.GzipFile(fileobj=f_in, mode="rb") as gz:
                    async with aiofiles.open(destination, "wb") as f_out:
                        await f_out.write(gz.read())
        except IOError as e:
            raise IOError(f"Ошибка при распаковке файла: {e}")

    @staticmethod
    async def decompress_zip(source: Path, destination: Path) -> None:
        """Асинхронная распаковка файла из формата Zip.

        Args:
            source (Path): Путь к сжатому файлу.
            destination (Path): Путь к распакованному файлу.

        Raises:
            FileNotFoundError: Если сжатый файл не найден.
            IOError: Если произошла ошибка при распаковке файла.
        """
        if not source.exists():
            raise FileNotFoundError(f"Файл {source} не найден")

        try:
            with zipfile.ZipFile(source, "r") as zipf:
                zipf.extractall(destination)
        except IOError as e:
            raise IOError(f"Ошибка при распаковке файла: {e}")

    @staticmethod
    async def decompress_rar(source: Path, destination: Path) -> None:
        """Асинхронная распаковка файла из формата RAR.

        Args:
            source (Path): Путь к сжатому файлу.
            destination (Path): Путь к распакованному файлу.

        Raises:
            FileNotFoundError: Если сжатый файл не найден.
            IOError: Если произошла ошибка при распаковке файла.
        """
        if not source.exists():
            raise FileNotFoundError(f"Файл {source} не найден")

        try:
            with rarfile.RarFile(source, "r") as rar:
                rar.extractall(destination)
        except IOError as e:
            raise IOError(f"Ошибка при распаковке файла: {e}")

    @staticmethod
    async def decompress_7z(source: Path, destination: Path) -> None:
        """Асинхронная распаковка файла из формата 7z.

        Args:
            source (Path): Путь к сжатому файлу.
            destination (Path): Путь к распакованному файлу.

        Raises:
            FileNotFoundError: Если сжатый файл не найден.
            IOError: Если произошла ошибка при распаковке файла.
        """
        if not source.exists():
            raise FileNotFoundError(f"Файл {source} не найден")

        try:
            with py7zr.SevenZipFile(source, "r") as archive:
                archive.extractall(destination)
        except IOError as e:
            raise IOError(f"Ошибка при распаковке файла: {e}")

    @staticmethod
    async def decompress_tar(source: Path, destination: Path) -> None:
        """Асинхронная распаковка файла из формата Tar.

        Args:
            source (Path): Путь к сжатому файлу.
            destination (Path): Путь к распакованному файлу.

        Raises:
            FileNotFoundError: Если сжатый файл не найден.
            IOError: Если произошла ошибка при распаковке файла.
        """
        if not source.exists():
            raise FileNotFoundError(f"Файл {source} не найден")

        try:
            with tarfile.open(source, "r:*") as tar:
                tar.extractall(destination)
        except IOError as e:
            raise IOError(f"Ошибка при распаковке файла: {e}")

    async def verify_integrity(self, source: Path) -> bool:
        """Проверка целостности сжатого файла.

        Args:
            source (Path): Путь к сжатому файлу.

        Returns:
            bool: True, если файл целостный, иначе False.

        Raises:
            FileNotFoundError: Если файл не найден.
        """
        if not source.exists():
            raise FileNotFoundError(f"Файл {source} не найден")

        try:
            if source.suffix == ".gz":
                with gzip.GzipFile(source, "rb") as gz:
                    gz.read()
            elif source.suffix == ".zip":
                with zipfile.ZipFile(source, "r") as zipf:
                    zipf.testzip()
            elif source.suffix == ".rar":
                with rarfile.RarFile(source, "r") as rar:
                    rar.testrar()
            elif source.suffix == ".7z":
                with py7zr.SevenZipFile(source, "r") as archive:
                    archive.test()
            elif source.suffix in (".tar", ".tar.gz", ".tar.bz2", ".tar.xz"):
                with tarfile.open(source, "r:*") as tar:
                    tar.getmembers()
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {source.suffix}")
            return True
        except Exception as e:
            if self.logger:
                self.logger(
                    f"Ошибка проверки целостности файла {source}: {e}", LogLevel.ERROR
                )
            return False
