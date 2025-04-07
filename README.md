# TurboPrint

Высокопроизводительная библиотека логирования для Python с поддержкой асинхронности.

## Возможности

-   Поддержка асинхронного логирования
-   Цветной вывод
-   Несколько уровней логирования
-   Простая настройка
-   Поддержка аннотаций типов

## Установка

```bash
pip install turbo-print
```

## Быстрый старт

```python
from turbo_print import TurboPrint

logger = TurboPrint()
logger.info("Привет, мир!")
```

## Настройка

Вы можете настроить логгер с разными уровнями логирования:

```python
from turbo_print import TurboPrint, LogLevel

logger = TurboPrint()
logger.set_level(LogLevel.DEBUG)
```

## Уровни логирования

-   DEBUG (Отладка)
-   INFO (Информация)
-   WARNING (Предупреждение)
-   ERROR (Ошибка)

## Требования

-   Python 3.10+
-   nest-asyncio
-   colorama
-   typing-extensions

## Лицензия

MIT License
