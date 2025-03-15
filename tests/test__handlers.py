from asyncio import get_event_loop
import unittest
import sys
from pathlib import Path
from datetime import datetime
from tempfile import TemporaryDirectory
from src.handlers import StreamHandler, FileHandler
from src.my_types import LogLevel, LogRecord, TurboPrintOutput


class TestStreamHandler(unittest.TestCase):
    def test_handle(self) -> None:
        handler = StreamHandler()
        record: LogRecord = {
            "message": "Test",
            "level": LogLevel.INFO,
            "name": "test",
            "prefix": "TEST",
            "timestamp": datetime.now(),
            "parent": None,
            "extra": {},
        }
        formatted: TurboPrintOutput = {
            "colored_console": "[INFO] Test",
            "standard_file": "[INFO] Test",
        }
        handler.handle(record, formatted, sys.stdout, sys.stderr)


class TestFileHandler(unittest.TestCase):
    def test_handle(self) -> None:
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
            }
            formatted: TurboPrintOutput = {
                "colored_console": "[INFO] Test",
                "standard_file": "[INFO] Test",
            }
            get_event_loop().run_until_complete(
                handler.handle(record, formatted, sys.stdout, sys.stderr)
            )
            self.assertTrue((Path(tmpdir) / "root_1.log").exists())
