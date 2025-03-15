import json
from pathlib import Path
from typing import Dict, Any
import yaml
from configparser import ConfigParser

from src.turbo_print import TurboPrint
from src.handlers import (
    StreamHandler,
    FileHandler,
    TimedRotatingFileHandler,
    SizeRotatingFileHandler,
)
from src.formatters import (
    DefaultFormatter,
    JSONFormatter,
    XMLFormatter,
    YAMLFormatter,
    CSVFormatter,
    HTMLFormatter,
    MarkdownFormatter,
)
from src.filters import (
    LevelFilter,
    RegexFilter,
    TimeFilter,
    ModuleFilter,
    CompositeFilter,
)
from src.my_types import LogLevel


class ConfigLoader:
    """Класс для загрузки конфигурации логгера из файлов."""

    @staticmethod
    def from_json(file_path: Path) -> Dict[str, Any]:
        """Загружает конфигурацию из JSON файла."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def from_yaml(file_path: Path) -> Dict[str, Any]:
        """Загружает конфигурацию из YAML файла."""
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def from_ini(file_path: Path) -> Dict[str, Any]:
        """Загружает конфигурацию из INI файла."""
        config = ConfigParser()
        config.read(file_path)
        return {section: dict(config[section]) for section in config.sections()}

    @staticmethod
    def configure_logger_from_file(file_path: Path) -> TurboPrint:
        """Создает и настраивает логгер на основе конфигурации из файла."""
        if file_path.suffix == ".json":
            config = ConfigLoader.from_json(file_path)
        elif file_path.suffix in (".yaml", ".yml"):
            config = ConfigLoader.from_yaml(file_path)
        elif file_path.suffix == ".ini":
            config = ConfigLoader.from_ini(file_path)
        else:
            raise ValueError("Неподдерживаемый формат файла")

        return ConfigLoader._create_logger_from_config(config)

    @staticmethod
    def _create_logger_from_config(config: Dict[str, Any]) -> TurboPrint:
        """Создает логгер на основе конфигурации."""
        logger_name = config.get("name", "root")
        logger = TurboPrint.get_logger(logger_name)

        # Настройка уровня логирования
        if "level" in config:
            logger.set_level(LogLevel[config["level"]])

        # Настройка форматтера
        if "formatter" in config:
            formatter_config = config["formatter"]
            formatter_type = formatter_config.get("type", "default")
            if formatter_type == "json":
                logger.set_formatter(JSONFormatter())
            elif formatter_type == "xml":
                logger.set_formatter(XMLFormatter())
            elif formatter_type == "yaml":
                logger.set_formatter(YAMLFormatter())
            elif formatter_type == "csv":
                logger.set_formatter(CSVFormatter())
            elif formatter_type == "html":
                logger.set_formatter(HTMLFormatter())
            elif formatter_type == "markdown":
                logger.set_formatter(MarkdownFormatter())
            else:
                logger.set_formatter(DefaultFormatter())

        # Настройка обработчиков
        if "handlers" in config:
            for handler_config in config["handlers"]:
                handler_type = handler_config.get("type")
                if handler_type == "stream":
                    handler = StreamHandler()
                elif handler_type == "file":
                    handler = FileHandler(
                        Path(handler_config.get("file_directory", "logs"))
                    )
                elif handler_type == "timed_rotating_file":
                    handler = TimedRotatingFileHandler(
                        Path(handler_config.get("file_directory", "logs")),
                        when=handler_config.get("when", "D"),
                        interval=handler_config.get("interval", 1),
                        backup_count=handler_config.get("backup_count", 5),
                    )
                elif handler_type == "size_rotating_file":
                    handler = SizeRotatingFileHandler(
                        Path(handler_config.get("file_directory", "logs")),
                        max_size=handler_config.get(
                            "max_size", 10 * 1024 * 1024
                        ),  # 10 MB
                        backup_count=handler_config.get("backup_count", 5),
                    )
                else:
                    raise ValueError(
                        f"Неподдерживаемый тип обработчика: {handler_type}"
                    )

                # Настройка фильтров для обработчика
                if "filters" in handler_config:
                    for filter_config in handler_config["filters"]:
                        filter_type = filter_config.get("type")
                        if filter_type == "level":
                            handler.add_filter(
                                LevelFilter(LogLevel[filter_config.get("level")])
                            )
                        elif filter_type == "regex":
                            handler.add_filter(
                                RegexFilter(filter_config.get("pattern"))
                            )
                        elif filter_type == "time":
                            handler.add_filter(
                                TimeFilter(
                                    start_time=filter_config.get("start_time"),
                                    end_time=filter_config.get("end_time"),
                                )
                            )
                        elif filter_type == "module":
                            handler.add_filter(
                                ModuleFilter(filter_config.get("module_name"))
                            )
                        elif filter_type == "composite":
                            handler.add_filter(
                                CompositeFilter(
                                    filters=[
                                        ConfigLoader._create_filter(f)
                                        for f in filter_config.get("filters", [])
                                    ],
                                    mode=filter_config.get("mode", "AND"),
                                )
                            )
                        else:
                            raise ValueError(
                                f"Неподдерживаемый тип фильтра: {filter_type}"
                            )

                logger.add_handler(handler)

        return logger

    @staticmethod
    def _create_filter(filter_config: Dict[str, Any]) -> BaseFilter:
        """Создает фильтр на основе конфигурации."""
        filter_type = filter_config.get("type")
        if filter_type == "level":
            return LevelFilter(LogLevel[filter_config.get("level")])
        elif filter_type == "regex":
            return RegexFilter(filter_config.get("pattern"))
        elif filter_type == "time":
            return TimeFilter(
                start_time=filter_config.get("start_time"),
                end_time=filter_config.get("end_time"),
            )
        elif filter_type == "module":
            return ModuleFilter(filter_config.get("module_name"))
        elif filter_type == "composite":
            return CompositeFilter(
                filters=[
                    ConfigLoader._create_filter(f)
                    for f in filter_config.get("filters", [])
                ],
                mode=filter_config.get("mode", "AND"),
            )
        else:
            raise ValueError(f"Неподдерживаемый тип фильтра: {filter_type}")
