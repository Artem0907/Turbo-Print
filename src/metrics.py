from typing import Dict, Any
from datetime import datetime
from prometheus_client import Counter, Gauge, start_http_server

class Metrics:
    """Класс для сбора и экспорта метрик."""

    def __init__(self):
        # Счетчики для метрик
        self.log_count = Counter("log_count", "Общее количество записей в логах", ["level"])
        self.error_count = Counter("error_count", "Общее количество ошибок")
        self.log_processing_time = Gauge("log_processing_time", "Время обработки записи в секундах")

        # Запуск HTTP-сервера для Prometheus
        start_http_server(8000)

    def log_processed(self, level: str, processing_time: float) -> None:
        """Метод для обновления метрик после обработки записи."""
        self.log_count.labels(level=level).inc()
        self.log_processing_time.set(processing_time)

    def error_occurred(self) -> None:
        """Метод для обновления счетчика ошибок."""
        self.error_count.inc()

    def get_metrics(self) -> Dict[str, Any]:
        """Возвращает текущие метрики в виде словаря."""
        return {
            "log_count": {level: self.log_count.labels(level=level)._value.get() for level in ["INFO", "ERROR"]},
            "error_count": self.error_count._value.get(),
            "log_processing_time": self.log_processing_time._value.get(),
        }