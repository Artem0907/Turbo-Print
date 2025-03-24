import unittest
from datetime import datetime
from ..src.formatters import DefaultFormatter, JSONFormatter
from ..src.my_types import LogLevel, LogRecord

class TestDefaultFormatter(unittest.TestCase):
    async def test_format(self) -> None:
        formatter = DefaultFormatter()
        record: LogRecord = {
            "message": "Test",
            "level": LogLevel.INFO,
            "name": "test",
            "prefix": "TEST",
            "timestamp": datetime.now(),
            "parent": None,
            "extra": {},
            "tags": [],
            "category": None
        }
        formatted = await formatter.format(record)
        self.assertIn("INFO", formatted)

class TestJSONFormatter(unittest.TestCase):
    async def test_format(self) -> None:
        formatter = JSONFormatter()
        record: LogRecord = {
            "message": "Test",
            "level": LogLevel.INFO,
            "name": "test",
            "prefix": "TEST",
            "timestamp": datetime.now(),
            "parent": None,
            "extra": {},
            "tags": [],
            "category": None
        }
        formatted = await formatter.format(record)
        self.assertIn('"level": "INFO"', formatted)