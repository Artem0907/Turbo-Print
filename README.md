# TurboPrint

TurboPrint — мощная и гибкая система логирования для Python.

## Основные возможности

-   Иерархические логгеры с поддержкой наследования настроек.
-   Поддержка цветного вывода в консоль.
-   Ротация лог-файлов по размеру и времени.
-   Асинхронная отправка логов в Telegram.
-   Гибкая система фильтрации и форматирования.

## Установка

```bash
pip install turbo-print
```

## Быстрый старт

```python
from turbo_print import TurboPrint, LogLevel
from turbo_print.handlers import StreamHandler
from pathlib import Path

# Создание логгера
logger = TurboPrint.get_logger("app")
logger.add_handler(StreamHandler())

# Логирование
logger("Запуск приложения", LogLevel.INFO)
logger("Ошибка подключения к базе данных", LogLevel.ERROR)
```

## Примеры

### Логирование в файл

```python
from turbo_print.handlers import FileHandler

logger.add_handler(FileHandler(Path("logs"), "app"))
logger("Это сообщение будет записано в файл", LogLevel.INFO)
```

### Логирование в реальном времени

```python
from turbo_print.realtime import RealTimeLogger

realtime_logger = RealTimeLogger()
realtime_logger.start_web_interface(host="0.0.0.0", port=5000)

logger = TurboPrint.get_logger("app", realtime_logger=realtime_logger)
logger("Это сообщение будет отображено в реальном времени", LogLevel.INFO)
```

## Документация

Подробная документация доступна в [документации](docs/README.md).
