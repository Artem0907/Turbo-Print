import logging
from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, Optional, Union
import aiofiles
import configparser
import json
import toml
import yaml
import xml.etree.ElementTree as ET
import csv
import os
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

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint


class ConfigLoader:
    """Класс для загрузки конфигурации логгера из файлов, строк и словарей."""

    @staticmethod
    async def from_json(file_path: Union[Path, str]) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из JSON файла или строки.

        Args:
            file_path (Union[Path, str]): Путь к JSON файлу или JSON-строка.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            json.JSONDecodeError: Если файл содержит некорректный JSON.
        """
        try:
            if isinstance(file_path, Path):
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
            else:
                content = file_path
            return json.loads(content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Некорректный JSON в файле {file_path}", e.doc, e.pos
            ) from e

    @staticmethod
    async def from_yaml(file_path: Union[Path, str]) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из YAML файла или строки.

        Args:
            file_path (Union[Path, str]): Путь к YAML файлу или YAML-строка.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            yaml.YAMLError: Если файл содержит некорректный YAML.
        """
        try:
            if isinstance(file_path, Path):
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
            else:
                content = file_path
            return yaml.safe_load(content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Некорректный YAML в файле {file_path}") from e

    @staticmethod
    async def from_ini(file_path: Union[Path, str]) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из INI файла или строки.

        Args:
            file_path (Union[Path, str]): Путь к INI файлу или INI-строка.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            configparser.Error: Если файл содержит некорректный INI.
        """
        config = ConfigParser()
        try:
            if isinstance(file_path, Path):
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
            else:
                content = file_path
            config.read_string(content)
            return {section: dict(config[section]) for section in config.sections()}
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except configparser.Error as e:
            raise configparser.Error(f"Некорректный INI в файле {file_path}") from e

    @staticmethod
    async def from_toml(file_path: Union[Path, str]) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из TOML файла или строки.

        Args:
            file_path (Union[Path, str]): Путь к TOML файлу или TOML-строка.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            toml.TomlDecodeError: Если файл содержит некорректный TOML.
        """
        try:
            if isinstance(file_path, Path):
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
            else:
                content = file_path
            return toml.loads(content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except toml.TomlDecodeError as e:
            raise toml.TomlDecodeError(f"Некорректный TOML в файле {file_path}") from e

    @staticmethod
    async def from_xml(file_path: Union[Path, str]) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из XML файла или строки.

        Args:
            file_path (Union[Path, str]): Путь к XML файлу или XML-строка.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            xml.etree.ElementTree.ParseError: Если файл содержит некорректный XML.
        """
        try:
            if isinstance(file_path, Path):
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
            else:
                content = file_path
            root = ET.fromstring(content)
            return {elem.tag: elem.text for elem in root}
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except ET.ParseError as e:
            raise ET.ParseError(f"Некорректный XML в файле {file_path}") from e

    @staticmethod
    async def from_csv(file_path: Union[Path, str]) -> Dict[str, Any]:
        """Асинхронно загружает конфигурацию из CSV файла или строки.

        Args:
            file_path (Union[Path, str]): Путь к CSV файлу или CSV-строка.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.

        Raises:
            FileNotFoundError: Если файл не найден.
            csv.Error: Если файл содержит некорректный CSV.
        """
        try:
            if isinstance(file_path, Path):
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
            else:
                content = file_path
            reader = csv.DictReader(content.splitlines())
            return {row["key"]: row["value"] for row in reader}
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e
        except csv.Error as e:
            raise csv.Error(f"Некорректный CSV в файле {file_path}") from e

    @staticmethod
    async def from_env() -> Dict[str, Any]:
        """Загружает конфигурацию из переменных окружения.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.
        """
        return {
            key: value for key, value in os.environ.items() if key.startswith("LOG_")
        }

    @staticmethod
    async def from_dict(config: Dict[str, Any]) -> Dict[str, Any]:
        """Загружает конфигурацию из словаря.

        Args:
            config (Dict[str, Any]): Словарь с конфигурацией.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.
        """
        return config

    @staticmethod
    async def configure_logger_from_file(
        file_path: Path, logger: Optional["TurboPrint"] = None
    ) -> "TurboPrint":
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
            elif file_path.suffix == ".xml":
                config = await ConfigLoader.from_xml(file_path)
            elif file_path.suffix == ".csv":
                config = await ConfigLoader.from_csv(file_path)
            else:
                raise ValueError("Неподдерживаемый формат файла")

            return await ConfigLoader._create_logger_from_config(config, logger)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Файл {file_path} не найден") from e

    @staticmethod
    async def _create_logger_from_config(
        config: Dict[str, Any], logger: Optional["TurboPrint"] = None
    ) -> "TurboPrint":
        """Асинхронно создает логгер на основе конфигурации.

        Args:
            config (Dict[str, Any]): Конфигурация логгера.
            logger (Optional[TurboPrint]): Существующий логгер для обновления. Если None, создается новый.

        Returns:
            TurboPrint: Настроенный логгер.

        Raises:
            ValueError: Если конфигурация содержит некорректные данные.
        """
        try:
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
        except Exception as e:
            raise ValueError(f"Ошибка при создании логгера: {e}") from e

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

    @staticmethod
    async def save_config_to_file(config: Dict[str, Any], file_path: Path) -> None:
        """Асинхронно сохраняет конфигурацию в файл.

        Args:
            config (Dict[str, Any]): Конфигурация логгера.
            file_path (Path): Путь к файлу для сохранения.

        Raises:
            ValueError: Если формат файла не поддерживается.
        """
        try:
            if file_path.suffix == ".json":
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(json.dumps(config, indent=4))
            elif file_path.suffix in (".yaml", ".yml"):
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(yaml.dump(config, indent=4))
            elif file_path.suffix == ".ini":
                config_parser = ConfigParser()
                for section, options in config.items():
                    config_parser[section] = options
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(config_parser.write())
            elif file_path.suffix == ".toml":
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(toml.dumps(config))
            elif file_path.suffix == ".xml":
                root = ET.Element("config")
                for key, value in config.items():
                    elem = ET.SubElement(root, key)
                    elem.text = str(value)
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(ET.tostring(root, encoding="unicode"))
            elif file_path.suffix == ".csv":
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=config.keys())
                    await writer.writeheader()
                    await writer.writerow(config)
            else:
                raise ValueError("Неподдерживаемый формат файла")
        except Exception as e:
            raise ValueError(f"Ошибка при сохранении конфигурации: {e}") from e

    @staticmethod
    def from_cli_args(args: Dict[str, Any]) -> Dict[str, Any]:
        """Загружает конфигурацию из аргументов командной строки.

        Args:
            args (Dict[str, Any]): Аргументы командной строки.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией.
        """
        return {key: value for key, value in args.items() if key.startswith("log_")}
