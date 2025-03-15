from typing import Dict, Any
from threading import Thread
from queue import Queue
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
from colorama import Fore, Style

class RealTimeLogger:
    """Класс для логирования в реальном времени."""

    def __init__(self):
        self.log_queue = Queue()
        self.socketio = None
        self.thread = None

    def start_web_interface(self, host: str = "0.0.0.0", port: int = 5000) -> None:
        """Запускает веб-интерфейс для отображения логов в реальном времени."""
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
                self.socketio.emit("log", log)

        self.thread = Thread(target=emit_logs)
        self.thread.daemon = True
        self.thread.start()

        self.socketio.run(app, host=host, port=port)

    def log_to_terminal(self, record: Dict[str, Any]) -> None:
        """Логирует запись в терминал с подсветкой."""
        level_color = {
            "DEBUG": Fore.CYAN,
            "INFO": Fore.BLUE,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
        }.get(record["level"], Fore.WHITE)

        message = f"{level_color}{record['message']}{Style.RESET_ALL}"
        print(message)

    def log(self, record: Dict[str, Any]) -> None:
        """Добавляет запись в очередь для логирования в реальном времени."""
        self.log_queue.put(record)
        self.log_to_terminal(record)