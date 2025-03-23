import unittest
from datetime import datetime
from src.my_types import LogRecord, LogLevel
from src.filters import LevelFilter, RegexFilter, TimeFilter


class TestFilters(unittest.TestCase):
    def setUp(self) -> None:
        self.record = LogRecord(
            message="Test message",
            level=LogLevel.INFO,
            name="test",
            prefix=None,
            timestamp=datetime.now(),
            parent=None,
            extra={},
            tags=[],
            category=None,
        )

    async def test_level_filter(self) -> None:
        filter = LevelFilter(LogLevel.WARNING)
        self.record["level"] = LogLevel.ERROR
        self.assertTrue(await filter.filter(self.record))

        self.record["level"] = LogLevel.DEBUG
        self.assertFalse(await filter.filter(self.record))

    async def test_regex_filter(self) -> None:
        filter = RegexFilter(r"Test")
        self.assertTrue(await filter.filter(self.record))

        filter_inverted = RegexFilter(r"Test", invert=True)
        self.assertFalse(await filter_inverted.filter(self.record))

    def test_time_filter(self) -> None:
        from datetime import time

        morning_filter = TimeFilter(time(6, 0), time(12, 0))
        self.record["timestamp"] = datetime(2023, 1, 1, 10, 0)
        self.assertTrue(morning_filter.filter(self.record))


if __name__ == "__main__":
    unittest.main()
