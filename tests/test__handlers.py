import unittest
import sys
from pathlib import Path
from datetime import datetime
from tempfile import TemporaryDirectory
from ..src.handlers import StreamHandler, FileHandler
from ..src.my_types import LogLevel, LogRecord, TurboPrintOutput
from ..src.turbo_print import TurboPrint


class TestStreamHandler(unittest.TestCase):
    async def test_handle(self) -> None:
        handler = StreamHandler()
        record: LogRecord = {
            "message": "Test",
            "level": LogLevel.INFO,
            "name": "test",
            "prefix": "TEST",
            "timestamp": datetime.now(),
            "parent": None,
            "extra": {},
            "tags": [],
            "category": None,
        }
        await handler.handle(TurboPrint(), record, sys.stdout, sys.stderr)


class TestFileHandler(unittest.TestCase):
    async def test_handle(self) -> None:
        with TemporaryDirectory() as tmpdir:
            handler = FileHandler(Path(tmpdir), "root_{index}")
            record: LogRecord = {
                "message": "Test",
                "level": LogLevel.INFO,
                "name": "test",
                "prefix": "TEST",
                "timestamp": datetime.now(),
                "parent": None,
                "extra": {},
                "tags": [],
                "category": None,
            }
            await handler.handle(TurboPrint(), record, sys.stdout, sys.stderr)
            self.assertTrue((Path(tmpdir) / "root_1.log").exists())
