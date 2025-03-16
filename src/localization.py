from typing import Dict, Optional, Union
from datetime import datetime
from babel.dates import format_datetime
from babel.numbers import format_number
from src.turbo_print import TurboPrint
from src.my_types import LogLevel


class Localization:
    """Класс для поддержки локализации сообщений логов с асинхронными методами."""

    def __init__(
        self, locale: str = "en", realtime_logger: Optional[TurboPrint] = None
    ):
        """
        Args:
            locale (str): Локаль по умолчанию (например, "en" для английского, "ru" для русского).
            realtime_logger (Optional[TurboPrint]): Логгер для записи в реальном времени.
        """
        self.locale = locale
        self.realtime_logger = realtime_logger
        self.translations: Dict[str, Dict[str, str]] = {
            "en": {
                "error": "Error",
                "warning": "Warning",
                "info": "Info",
                "debug": "Debug",
                "critical": "Critical",
            },
            "ru": {
                "error": "Ошибка",
                "warning": "Предупреждение",
                "info": "Информация",
                "debug": "Отладка",
                "critical": "Критическая ошибка",
            },
            # Добавьте другие языки по необходимости
            "es": {
                "error": "Error",
                "warning": "Advertencia",
                "info": "Información",
                "debug": "Depuración",
                "critical": "Crítico",
            },
            "fr": {
                "error": "Erreur",
                "warning": "Avertissement",
                "info": "Information",
                "debug": "Débogage",
                "critical": "Critique",
            },
        }

    async def translate(self, key: str, **kwargs: Union[str, int, float]) -> str:
        """Асинхронно переводит ключ на текущий язык с поддержкой контекста.

        Args:
            key (str): Ключ для перевода.
            **kwargs: Переменные для подстановки в сообщение.

        Returns:
            str: Переведенное значение.
        """
        if self.realtime_logger:
            await self.realtime_logger.log(
                {
                    "message": f"Перевод ключа: {key}",
                    "level": "DEBUG",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        translation = self.translations.get(self.locale, {}).get(key, key)
        return translation.format(**kwargs) if kwargs else translation

    def format_datetime(self, dt: datetime, format: str = "medium") -> str:
        """Форматирует дату и время в соответствии с локалью.

        Args:
            dt (datetime): Дата и время для форматирования.
            format (str): Формат (например, "medium", "short").

        Returns:
            str: Отформатированная строка.
        """
        return format_datetime(dt, format=format, locale=self.locale)

    def format_number(self, number: Union[int, float]) -> str:
        """Форматирует число в соответствии с локалью.

        Args:
            number (Union[int, float]): Число для форматирования.

        Returns:
            str: Отформатированная строка.
        """
        return format_number(number, locale=self.locale)

    def set_locale(self, locale: str) -> None:
        """Устанавливает локаль для форматирования.

        Args:
            locale (str): Новая локаль.
        """
        self.locale = locale

    def get_locale(self) -> str:
        """Возвращает текущую локаль.

        Returns:
            str: Текущая локаль.
        """
        return self.locale
