from typing import Dict, Optional
from datetime import datetime
from babel.dates import format_datetime
from babel.numbers import format_number

class Localization:
    """Класс для поддержки локализации сообщений логов."""

    def __init__(self, locale: str = "en"):
        """
        Args:
            locale (str): Локаль по умолчанию (например, "en" для английского, "ru" для русского).
        """
        self.locale = locale
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
        }

    def translate(self, key: str) -> str:
        """Переводит ключ на текущий язык."""
        return self.translations.get(self.locale, {}).get(key, key)

    def format_datetime(self, dt: datetime, format: str = "medium") -> str:
        """Форматирует дату и время в соответствии с локалью."""
        return format_datetime(dt, format=format, locale=self.locale)

    def format_number(self, number: float) -> str:
        """Форматирует число в соответствии с локалью."""
        return format_number(number, locale=self.locale)