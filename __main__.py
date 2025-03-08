from pathlib import Path
from src.handlers import FileHandler, StreamHandler
from src.formatters import DefaultFormatter
from src.types import LogLevel
from src.turbo_print import TurboPrint

tp = TurboPrint(enabled=True, level=LogLevel.NOTSET, propagate=False)
tp.add_handler(FileHandler(Path("d:/python/function/logs"), max_size=1024 * 10))
tp.add_handler(StreamHandler())
tp._root_logger("...", LogLevel.WARN)


tp("starting app...", LogLevel.DEBUG)
tp("app started", LogLevel.LOG)
tp("stopping app...", LogLevel.DEBUG)
tp("app stopped", LogLevel.LOG)
tp("exiting app...", LogLevel.DEBUG)
tp("app exited", LogLevel.LOG)

print("done")
