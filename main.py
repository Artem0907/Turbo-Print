from colorama import Style
from faker import Faker
from pathlib import Path
from sys import maxsize

from src.my_types import LogLevel, LogRecord
from src.turbo_print import TurboPrint
from src import filters, formatters, handlers


class MyFormatter(formatters.BaseFormatter):
    def format(self, record: LogRecord) -> str:
        return record["message"]

    def format_colored(self, record: LogRecord) -> str:
        """Цветное форматирование записи."""
        return (
            record["level"].color
            + "["
            + record["timestamp"].strftime("%H:%M:%S")
            + "]"
            + record["name"]
            + " | "
            + record["level"].name
            + "["
            + str(record["level"].value)
            + "]: "
            + record["message"]
            + Style.RESET_ALL
        )


root_logger = TurboPrint.get_logger()
root_logger.level = LogLevel.NOTSET


main_logger = TurboPrint(
    "main",
    enabled=True,
    prefix="MAIN",
    level=LogLevel.NOTSET,
    parent=None,
    propagate=False,
)
main_logger.add_handler(
    handlers.FileHandler(
        Path("./logs"),
        "__main___{index}",
        max_size=100 * 1024,  # 100kb
        max_lines=10000,
    )
)
# main_logger.add_handler(StreamHandler())
# main_logger.level = LogLevel.LOG

test_logger = TurboPrint(
    "test",
    enabled=True,
    prefix="TEST",
    level=LogLevel.NOTSET,
    parent=main_logger,
    propagate=False,
)
test_logger.add_handler(
    handlers.StreamHandler(
        open(
            "./logs/TEST.txt",
            "a",
            -1,
            "utf-8",
            newline="\n",
        ),
        False,
    )
)
test_logger.add_handler(handlers.StreamHandler())
test_logger.set_formatter(MyFormatter())
# test_logger.level = LogLevel.LOG


_CLASSES = [
    TurboPrint,
    root_logger,
    Path(
        "turbo_print/src/logs",
    ),
    Faker,
    TurboPrint(
        "test.my_name",
        enabled=True,
        prefix="TEST",
        level=LogLevel.DEBUG,
        parent=None,
        propagate=False,
        handlers=None,
        filters=None,
        formatter=formatters.DefaultFormatter(
            fmt="[{time}] {prefix} | {level_name}[{level_value}]: {message}",
        ),
    ),
]
for test_id, test_name in enumerate(_CLASSES):
    if test_name.__class__ == type:
        test_logger(
            f"{test_name.__name__} = {str(test_name)}",
            LogLevel.DEBUG,
        )
        test_logger(
            f"repr({test_name.__name__}) = {repr(test_name)}",
            LogLevel.DEBUG,
        )
        root_logger(
            f"[{test_id+1}/{len(_CLASSES)}] {test_name.__name__}",
            LogLevel.SUCCESS,
        )
    else:
        test_logger(
            f"{test_name.__class__.__name__} = {str(test_name)}",
            LogLevel.DEBUG,
        )
        test_logger(
            f"repr({test_name.__class__.__name__}) = {repr(test_name)}",
            LogLevel.DEBUG,
        )
        root_logger(
            f"[{test_id+1}/{len(_CLASSES)}] {test_name.__class__.__name__}",
            LogLevel.SUCCESS,
        )
print()


_NAME = "logger"
_OPERATIONS_ITERATIONS = int(
    input("Enter the number of iterations from check logger: ")
)
_OPERATIONS = ["start", "wait", "stopp", "restart", "exit", "delet"]
for iteration in range(_OPERATIONS_ITERATIONS):
    for operation_id, operation_name in enumerate(_OPERATIONS):
        main_logger(
            f"{operation_name}ing {_NAME}...",
            LogLevel.DEBUG,
        )
        main_logger(
            f"{_NAME} {operation_name}ed",
            LogLevel.INFO,
        )

        root_logger(
            (
                f"[{iteration+1}/{_OPERATIONS_ITERATIONS}]"
                + f"[{operation_id+1}/{len(_OPERATIONS)}] "
                + f'In "{main_logger.get_handlers()[0].current_file.name}" '  # type: ignore
                + f"From {repr(main_logger)} "
                + f"[{operation_name}]"
            ),
            LogLevel.SUCCESS,
        )
print()


dir_1_logger = TurboPrint(
    name="dir_1",
    enabled=True,
    prefix="DIR_1",
    level=LogLevel.NOTSET,
    parent=main_logger,
    propagate=False,
    handlers=[
        handlers.FileHandler(
            file_directory=Path(
                "./logs/",
            ),
            file_name="test_dir_{index}",
            max_size=(1 * 1024 * 1024 * 1024),
            max_lines=1000000,
        ),
        handlers.StreamHandler(),
    ],
    filters=None,
    formatter=formatters.DefaultFormatter(
        fmt="[{time}] {prefix} | {level_name}[{level_value}]: {message}",
    ),
)
dir_2_logger = TurboPrint(
    name="dir_2",
    enabled=True,
    prefix="DIR_2",
    level=LogLevel.NOTSET,
    parent=main_logger,
    propagate=False,
    handlers=[
        handlers.FileHandler(
            file_directory=Path(
                "./logs/",
            ),
            file_name="test_dir_{index}",
            max_size=(10 * 1024),
            max_lines=1000,
        ),
        handlers.StreamHandler(),
    ],
    filters=None,
    formatter=formatters.DefaultFormatter(
        fmt="[{time}] {prefix} | {level_name}[{level_value}]: {message}",
    ),
)

_FILE_ITERATIONS = int(input("Enter the number of iterations from check files: "))
for iterations in range(_FILE_ITERATIONS):
    dir_1_logger(
        f"test message in {dir_1_logger.handlers[0].current_file} for `dir logger 1` [{iterations+1}/{_FILE_ITERATIONS}]",  # type: ignore
        LogLevel.DEBUG,
    )
    dir_2_logger(
        f"test message in {dir_2_logger.handlers[0].current_file} for `dir logger 2` [{iterations+1}/{_FILE_ITERATIONS}]",  # type: ignore
        LogLevel.DEBUG,
    )
print()


file_handler = handlers.FileHandler(
    file_directory=Path(
        "./logs/",
    ),
    file_name="test_2_dir_{index}",
    max_size=maxsize,
    max_lines=maxsize,
)
dir2_1_logger = TurboPrint(
    name="dir2_1",
    enabled=True,
    prefix="DIR2_1",
    level=LogLevel.NOTSET,
    parent=main_logger,
    propagate=False,
    handlers=[
        file_handler,
        handlers.StreamHandler(),
    ],
    filters=None,
    formatter=formatters.DefaultFormatter(
        fmt="[{time}] {prefix} | {level_name}[{level_value}]: {message}",
    ),
)
dir2_2_logger = TurboPrint(
    name="dir2_2",
    enabled=True,
    prefix="DIR2_2",
    level=LogLevel.NOTSET,
    parent=main_logger,
    propagate=False,
    handlers=[
        file_handler,
        handlers.StreamHandler(),
    ],
    filters=None,
    formatter=formatters.DefaultFormatter(
        fmt="[{time}] {prefix} | {level_name}[{level_value}]: {message}",
    ),
)

_FILE_ITERATIONS = int(input("Enter the number of iterations from check file: "))
for iterations in range(_FILE_ITERATIONS):
    dir2_1_logger(
        f"test message in {dir2_1_logger.handlers[0].current_file} for `dir2 logger 1` [{iterations+1}/{_FILE_ITERATIONS}]",  # type: ignore
        LogLevel.DEBUG,
    )
    dir2_2_logger(
        f"test message in {dir2_2_logger.handlers[0].current_file} for `dir2 logger 2` [{iterations+1}/{_FILE_ITERATIONS}]",  # type: ignore
        LogLevel.DEBUG,
    )
