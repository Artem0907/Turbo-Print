from pathlib import Path, WindowsPath
from faker import Faker

from src.filters import LevelFilter
from src.handlers import FileHandler, StreamHandler
from src.formatters import DefaultFormatter
from src.my_types import LogLevel
from src.turbo_print import TurboPrint


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
    FileHandler(
        Path("./logs"),
        "__main___{index}",
        max_size=100 * 1024,  # 100kb
        max_lines=10000,
    )
)
# main_logger.level = LogLevel.LOG
# main_logger.add_handler(StreamHandler())

test_logger = TurboPrint(
    "test",
    enabled=True,
    prefix="TEST",
    level=LogLevel.NOTSET,
    parent=main_logger,
    propagate=False,
)
test_logger.add_handler(StreamHandler())
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
        formatter=DefaultFormatter(
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
                f"[{iteration+1}/{_ITERATIONS}]"
                + f"[{operation_id+1}/{len(_OPERATIONS)}]"
                + f'In "{main_logger.get_handlers()[-1].current_file.name}" '  # type: ignore
                + f"From {repr(main_logger)}"
            ),
            LogLevel.SUCCESS,
        )


dir_1_logger = TurboPrint(
    name="dir_1",
    enabled=True,
    prefix="DIR_1",
    level=LogLevel.DEBUG,
    parent=main_logger,
    propagate=False,
    handlers=[
        FileHandler(
            file_directory=Path(
                "./logs/",
            ),
            file_name="test_dir_{index}",
            max_size=(1 * 1024 * 1024 * 1024),
            max_lines=1000000,
        ),
        StreamHandler(),
    ],
    filters=None,
    formatter=DefaultFormatter(
        fmt="[{time}] {prefix} | {level_name}[{level_value}]: {message}",
    ),
)
dir_2_logger = TurboPrint(
    name="dir_2",
    enabled=True,
    prefix="DIR_2",
    level=LogLevel.DEBUG,
    parent=main_logger,
    propagate=False,
    handlers=[
        FileHandler(
            file_directory=Path(
                "./logs/",
            ),
            file_name="test_dir_{index}",
            max_size=(10 * 1024),
            max_lines=1000,
        ),
        StreamHandler(),
    ],
    filters=None,
    formatter=DefaultFormatter(
        fmt="[{time}] {prefix} | {level_name}[{level_value}]: {message}",
    ),
)

print("\n")
_FILE_ITERATIONS = int(input("Enter the number of iterations from check file: "))
for iterations in range(_FILE_ITERATIONS):
    dir_1_logger(
        f"test message in {dir_1_logger.handlers[0].current_file} for `dir logger 1` [{iterations+1}/{_FILE_ITERATIONS}]",
        LogLevel.DEBUG,
    )
    dir_2_logger(
        f"test message in {dir_2_logger.handlers[0].current_file} for `dir logger 2` [{iterations+1}/{_FILE_ITERATIONS}]",
        LogLevel.DEBUG,
    )

FileHandler(Path("."), "test")
