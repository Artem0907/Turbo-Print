from typing import TYPE_CHECKING, Any, Optional
from datetime import datetime
from prometheus_client import Counter, Gauge, start_http_server

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint


class Metrics:
    """Класс для сбора и экспорта метрик с поддержкой асинхронности."""

    def __init__(self, realtime_logger: Optional["TurboPrint"] = None):
        """
        Args:
            realtime_logger (Optional[TurboPrint]): Логгер для записи в реальном времени.
        """
        # Счетчики для метрик
        self.log_count = Counter(
            "log_count", "Общее количество записей в логах", ["level"]
        )
        self.error_count = Counter("error_count", "Общее количество ошибок")
        self.log_processing_time = Gauge(
            "log_processing_time", "Время обработки записи в секундах"
        )
        self.realtime_logger = realtime_logger

        # Запуск HTTP-сервера для Prometheus
        start_http_server(8000)

    async def log_processed(self, level: str, processing_time: float) -> None:
        """Асинхронное обновление метрик после обработки записи.

        Args:
            level (str): Уровень логирования.
            processing_time (float): Время обработки записи в секундах.
        """
        if self.realtime_logger:
            await self.realtime_logger.log(
                {
                    "message": f"Запись лога уровня {level} обработана за {processing_time:.2f} секунд",
                    "level": "INFO",
                    "timestamp": datetime.now(),
                }
            )
        self.log_count.labels(level=level).inc()
        self.log_processing_time.set(processing_time)

    async def error_occurred(self) -> None:
        """Асинхронное обновление счетчика ошибок."""
        if self.realtime_logger:
            await self.realtime_logger.log(
                {
                    "message": "Произошла ошибка",
                    "level": "ERROR",
                    "timestamp": datetime.now(),
                }
            )
        self.error_count.inc()

    async def get_metrics(self) -> dict[str, Any]:
        """Асинхронное получение текущих метрик в виде словаря.

        Returns:
            Dict[str, Any]: Словарь с метриками.
        """
        return {
            "log_count": {
                level: self.log_count.labels(level=level)._value.get()
                for level in ["INFO", "ERROR"]
            },
            "error_count": self.error_count._value.get(),
            "log_processing_time": self.log_processing_time._value.get(),
        }


class CustomMetrics(Metrics):
    """Класс для создания пользовательских метрик."""

    def __init__(self, realtime_logger: Optional["TurboPrint"] = None):
        """
        Args:
            realtime_logger (Optional[TurboPrint]): Логгер для записи в реальном времени.
        """
        super().__init__(realtime_logger)
        self.custom_counter = Counter("custom_counter", "Пользовательский счетчик")

    async def increment_custom_counter(self) -> None:
        """Асинхронное увеличение пользовательского счетчика."""
        self.custom_counter.inc()
        if self.realtime_logger:
            await self.realtime_logger.log(
                {
                    "message": "Пользовательский счетчик увеличен",
                    "level": "INFO",
                    "timestamp": datetime.now(),
                }
            )
