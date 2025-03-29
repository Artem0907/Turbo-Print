from typing import TYPE_CHECKING, Literal, Optional, Union
from datetime import datetime
from babel import Locale
from babel.dates import format_datetime, get_timezone
from babel.numbers import format_number

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint


class Localization:
    """Класс для поддержки локализации сообщений логов с асинхронными методами."""

    def __init__(
        self,
        locale: Literal["ru", "en"] = "ru",
        realtime_logger: Optional["TurboPrint"] = None,
    ):
        """
        Args:
            locale (str): Локаль по умолчанию (например, "en" для английского, "ru" для русского).
            realtime_logger (Optional[TurboPrint]): Логгер для записи в реальном времени.
        """
        self._translation_cache = {}
        self.locale = locale
        self.realtime_logger = realtime_logger
        self.translations: dict[str, dict[str, str]] = {
            "en": {
                "notset": "Not set",
                "trace": "Trace",
                "debug": "Debug",
                "info": "Info",
                "notice": "Notice",
                "success": "Success",
                "warning": "Warning",
                "error": "Error",
                "critical": "Critical",
                "security": "Security",
            },
            "ru": {
                "notset": "Не установлен",
                "trace": "Трассировка",
                "debug": "Логирование",
                "info": "Информация",
                "notice": "Сообщение",
                "success": "Успешно",
                "warning": "Предупреждение",
                "error": "Ошибка",
                "critical": "Критическая ошибка",
                "security": "Безопасность",
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
        cache_key = f"{key}_{self.locale}_{str(kwargs)}"
        if cache_key not in self._translation_cache:
            if self.realtime_logger:
                await self.realtime_logger.log(
                    {
                        "message": f"Перевод ключа: {key}",
                        "level": "DEBUG",
                        "timestamp": datetime.now(),
                    }
                )

            translation = self.translations.get(self.locale, {}).get(key, key)
            self._translation_cache[cache_key] = translation
        return (
            self._translation_cache[cache_key].format(**kwargs)
            if kwargs
            else self._translation_cache[cache_key]
        )

    def format_datetime(self, dt: datetime, format: str = "short") -> str:
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
