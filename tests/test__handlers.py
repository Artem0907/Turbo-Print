import unittest
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
        handler.handle(record, formatted)

class TestFileHandler(unittest.TestCase):
    def test_handle(self) -> None:
        with TemporaryDirectory() as tmpdir:
            handler = FileHandler(Path(tmpdir))
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
            handler.handle(record, formatted)
            self.assertTrue((Path(tmpdir) / "root_0.log").exists())