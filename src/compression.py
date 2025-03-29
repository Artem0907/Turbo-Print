from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import aiofiles
import aiofiles.os
from zipfile import ZipFile, ZIP_DEFLATED
from rarfile import RarFile

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint
from src.exceptions import CompressionError
from src.my_types import LogLevel


class BaseCompressor(ABC):
    """Абстрактный компрессор с общим поведением"""

    def __init__(self, logger: Optional["TurboPrint"] = None):
        self.logger = logger

    async def compress(self, source: Path, destination: Path) -> None:
        try:
            if not await self._validate_source(source):
                return
            
            await self._compress_impl(source, destination)
            await self._post_compress(source)
            
        except Exception as e:
            await self._handle_error(e, source)
            raise CompressionError(
                f"Failed to compress {source}",
                context={
                    "source": str(source),
                    "destination": str(destination),
                    "error": str(e)
                }
            )

    async def _validate_source(self, source: Path) -> bool:
        if not source.exists():
            error = f"File {source} not found"
            if self.logger:
                self.logger(error, LogLevel.ERROR)
            return False
        return True

    @abstractmethod
    async def _compress_impl(self, source: Path, destination: Path) -> None:
        pass

    async def _post_compress(self, source: Path) -> None:
        await aiofiles.os.remove(source)

    async def _handle_error(self, error: Exception, source: Path) -> None:
        error_msg = f"Error compressing {source}: {str(error)}"
        if self.logger:
            self.logger(error_msg, LogLevel.ERROR)
        raise RuntimeError(error_msg)


class ZipCompressor(BaseCompressor):
    def __init__(
        self, compression_level: int = 9, logger: Optional["TurboPrint"] = None
    ):
        super().__init__(logger)
        self.compression_level = compression_level

    async def _compress_impl(self, source: Path, destination: Path) -> None:
        async with aiofiles.open(source, "rb") as f_in:
            data = await f_in.read()

            with ZipFile(
                destination, "w", ZIP_DEFLATED, compresslevel=self.compression_level
            ) as zipf:
                zipf.writestr(source.name, data)


class RarCompressor(BaseCompressor):
    def __init__(
        self, compression_level: int = 5, logger: Optional["TurboPrint"] = None
    ):
        super().__init__(logger)
        self.compression_level = compression_level

    async def _compress_impl(self, source: Path, destination: Path) -> None:
        async with aiofiles.open(source, "rb") as f_in:
            data = await f_in.read()

            with RarFile(
                destination,
                "w",
            ) as rar:
                rar.open(source, "wb").write(data)
