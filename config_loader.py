from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Any, Optional
import aiofiles
import configparser
import json
import toml
import yaml
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
    BaseFilter,
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
    async def from_json(file_path: Path) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из JSON файла.

        Args:
            file_path (Path): Путь к JSON файлу.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            json.JSONDecodeError: Если файл содержит некорректный JSON.
        """
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Некорректный JSON в файле {file_path}", e.doc, e.pos
            ) from e

    @staticmethod
    async def from_yaml(file_path: Path) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из YAML файла.

        Args:
            file_path (Path): Путь к YAML файлу.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            yaml.YAMLError: Если файл содержит некорректный YAML.
        """
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                return yaml.safe_load(content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Некорректный YAML в файле {file_path}") from e

    @staticmethod
    async def from_ini(file_path: Path) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из INI файла.

        Args:
            file_path (Path): Путь к INI файлу.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            configparser.Error: Если файл содержит некорректный INI.
        """
        config = ConfigParser()
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                config.read_string(content)
                return {section: dict(config[section]) for section in config.sections()}
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except configparser.Error as e:
            raise configparser.Error(f"Некорректный INI в файле {file_path}") from e

    @staticmethod
    async def from_toml(file_path: Path) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из TOML файла.

        Args:
            file_path (Path): Путь к TOML файлу.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            toml.TomlDecodeError: Если файл содержит некорректный TOML.
        """
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                return toml.loads(content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except toml.TomlDecodeError as e:
            raise toml.TomlDecodeError(f"Некорректный TOML в файле {file_path}") from e

    @staticmethod
    async def configure_logger_from_file(
        file_path: Path, logger: Optional[TurboPrint] = None
    ) -> TurboPrint:
        """Асинхронно создает и настраивает логгер на основе конфигурации из файла.

        Args:
            file_path (Path): Путь к файлу конфигурации.
            logger (Optional[TurboPrint]): Существующий логгер для обновления. Если None, создается новый.

        Returns:
            TurboPrint: Настроенный логгер.

        Raises:
            ValueError: Если формат файла не поддерживается.
            FileNotFoundError: Если файл не найден.
        """
        try:
            if file_path.suffix == ".json":
                config = await ConfigLoader.from_json(file_path)
            elif file_path.suffix in (".yaml", ".yml"):
                config = await ConfigLoader.from_yaml(file_path)
            elif file_path.suffix == ".ini":
                config = await ConfigLoader.from_ini(file_path)
            elif file_path.suffix == ".toml":
                config = await ConfigLoader.from_toml(file_path)
            else:
                raise ValueError("Неподдерживаемый формат файла")

            return await ConfigLoader._create_logger_from_config(config, logger)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e

    @staticmethod
    async def _create_logger_from_config(
        config: Dict[str, Any], logger: Optional[TurboPrint] = None
    ) -> TurboPrint:
        """Асинхронно создает логгер на основе конфигурации.

        Args:
            config (Dict[str, Any]): Конфигурация логгера.
            logger (Optional[TurboPrint]): Существующий логгер для обновления. Если None, создается новый.

        Returns:
            TurboPrint: Настроенный логгер.
        """
        logger = logger or TurboPrint.get_logger(config.get("name", "root"))

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
                                RegexFilter(filter_config.get("pattern", ""))
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
                                ModuleFilter(filter_config.get("module_name", ""))
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
        """Создает фильтр на основе конфигурации.

        Args:
            filter_config (Dict[str, Any]): Конфигурация фильтра.

        Returns:
            BaseFilter: Созданный фильтр.

        Raises:
            ValueError: Если тип фильтра не поддерживается.
        """
        filter_type = filter_config.get("type")
        if filter_type == "level":
            return LevelFilter(LogLevel[filter_config.get("level")])
        elif filter_type == "regex":
            return RegexFilter(filter_config.get("pattern", ""))
        elif filter_type == "time":
            return TimeFilter(
                start_time=filter_config.get("start_time"),
                end_time=filter_config.get("end_time"),
            )
        elif filter_type == "module":
            return ModuleFilter(filter_config.get("module_name", ""))
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
