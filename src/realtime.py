from typing import TYPE_CHECKING, Any, Optional
from threading import Thread
from queue import Queue
from flask import Flask, render_template
from flask_socketio import SocketIO
from colorama import Fore, Style

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint
from src.my_types import LogLevel


class RealTimeLogger:
    """Класс для логирования в реальном времени с поддержкой асинхронности."""

    def __init__(self, logger: Optional["TurboPrint"] = None):
        """
        Args:
            logger (Optional[TurboPrint]): Логгер для записи ошибок.
        """
        self.log_queue = Queue(maxsize=1000)
        self.socketio = None
        self.thread = None
        self.logger = logger

    def start_web_interface(self, host: str = "0.0.0.0", port: int = 5000) -> None:
        """Запускает веб-интерфейс для отображения логов в реальном времени.

        Args:
            host (str): Хост для запуска веб-интерфейса.
            port (int): Порт для запуска веб-интерфейса.
        """
        app = Flask(__name__)
        self.socketio = SocketIO(app)

        @app.route("/")
        def index():
            return render_template("index.html")

        @self.socketio.on("connect")
        def handle_connect():
            print("Клиент подключен")

        def emit_logs():
            while True:
                log = self.log_queue.get()
                self.socketio.emit("log", log)  # type: ignore

        self.thread = Thread(target=emit_logs)
        self.thread.daemon = True
        self.thread.start()

        self.socketio.run(app, host=host, port=port)

    async def log_to_terminal(self, record: dict[str, Any]) -> None:
        """Асинхронное логирование записи в терминал с подсветкой.

        Args:
            record (Dict[str, Any]): Запись лога.
        """
        level_color = {
            "DEBUG": Fore.CYAN,
            "INFO": Fore.BLUE,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
        }.get(record["level"], Fore.WHITE)

        message = f"{level_color}{record['message']}{Style.RESET_ALL}"
        print(message)

    async def log(self, record: dict[str, Any]) -> None:
        """Асинхронное добавление записи в очередь для логирования в реальном времени.

        Args:
            record (Dict[str, Any]): Запись лога.
        """
        try:
            self.log_queue.put(record)
            await self.log_to_terminal(record)
        except Exception as e:
            error_msg = f"Ошибка при добавлении записи в очередь: {e}"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)


class CustomRealTimeLogger(RealTimeLogger):
    """Класс для создания пользовательских обработчиков логирования в реальном времени."""

    def __init__(self, logger: Optional["TurboPrint"] = None):
        """
        Args:
            logger (Optional[TurboPrint]): Логгер для записи ошибок.
        """
        super().__init__(logger)
        self.custom_queue = Queue()

    async def log_custom(self, record: dict[str, Any]) -> None:
        """Асинхронное добавление записи в пользовательскую очередь.

        Args:
            record (Dict[str, Any]): Запись лога.
        """
        try:
            self.custom_queue.put(record)
            await self.log_to_terminal(record)
        except Exception as e:
            error_msg = f"Ошибка при добавлении записи в пользовательскую очередь: {e}"
            if self.logger:
                self.logger(error_msg, LogLevel.ERROR)
