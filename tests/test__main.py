from pathlib import Path as _Path
from tempfile import TemporaryDirectory as _TemporaryDirectory
from unittest import TestCase as _TestCase

from src.handlers import StreamHandler as _StreamHandler, FileHandler as _FileHandler
from src.my_types import LogLevel as _LogLevel
from src.turbo_print import TurboPrint as _TurboPrint

__all__ = ["MainTestCase"]


class MainTestCase(_TestCase):
    def setUp(self) -> None:
        self.logger = _TurboPrint("test", level=_LogLevel.NOTSET)
        self.root_logger = _TurboPrint.get_logger()

        self.root_logger.level = _LogLevel.NOTSET
        self.file_directory = _TemporaryDirectory()

        self.file_handler = _FileHandler(
            _Path(self.file_directory.name), "test", max_size=1024, max_lines=10
        )
        self.stream_handler = _StreamHandler()

        self.logger.add_handler(self.stream_handler)
        self.logger.add_handler(self.file_handler)

    def tearDown(self) -> None:
        self.file_directory.cleanup()
