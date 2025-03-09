from pathlib import Path

from src.filters import LevelFilter
from src.handlers import FileHandler, StreamHandler
from src.formatters import DefaultFormatter
from src.my_types import LogLevel
from src.turbo_print import TurboPrint


root_logger = TurboPrint.get_logger()
main_logger = TurboPrint("main", enabled=True, level=LogLevel.NOTSET, propagate=False)
main_logger.add_handler(
    FileHandler(
        Path("d:/python/function/turbo_print/logs"),
        "__main__",
        max_size=50 * 1024,
        max_lines=1000,
    )
)
root_logger.level = LogLevel.NOTSET


# main_logger.level = LogLevel.LOG
# main_logger.add_handler(StreamHandler())


_NAME = "logger"
_ITERATIONS = int(input("Enter the number of iterations from check logger: "))
_OPERATIONS = ["start", "wait", "stopp", "restart", "exit", "delet"]

for iteration in range(_ITERATIONS):
    for operation_id, operation_name in enumerate(_OPERATIONS):
        main_logger(f"{operation_name}ing {_NAME}...", LogLevel.DEBUG)
        main_logger(f"{_NAME} {operation_name}ed", LogLevel.LOG)

        root_logger(
            (
                f"[{iteration+1}/{_ITERATIONS}]"
                + f"[{operation_id+1}/{len(_OPERATIONS)}]"
                + f"From {repr(main_logger)}"
            ),
            LogLevel.SUCCESS,
        )
