import gzip
import zipfile
from pathlib import Path
from typing import Union
import aiofiles
import aiofiles.os

class Compression:
    """Класс для сжатия логов."""

    @staticmethod
    async def compress_gzip(source: Path, destination: Path) -> None:
        """Сжимает файл в формате Gzip."""
        async with aiofiles.open(source, "rb") as f_in:
            async with aiofiles.open(destination, "wb") as f_out:
                async with gzip.open(f_out, "wb") as gz:
                    await gz.write(await f_in.read())
        await aiofiles.os.remove(source)

    @staticmethod
    async def compress_zip(source: Path, destination: Path) -> None:
        """Сжимает файл в формате Zip."""
        async with aiofiles.open(source, "rb") as f_in:
            async with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(source, arcname=source.name)
        await aiofiles.os.remove(source)

    @staticmethod
    async def decompress_gzip(source: Path, destination: Path) -> None:
        """Распаковывает файл из формата Gzip."""
        async with aiofiles.open(source, "rb") as f_in:
            async with gzip.open(f_in, "rb") as gz:
                async with aiofiles.open(destination, "wb") as f_out:
                    await f_out.write(await gz.read())

    @staticmethod
    async def decompress_zip(source: Path, destination: Path) -> None:
        """Распаковывает файл из формата Zip."""
        with zipfile.ZipFile(source, "r") as zipf:
            zipf.extractall(destination)