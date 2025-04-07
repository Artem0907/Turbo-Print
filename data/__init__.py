from atexit import register as _register_atexit
from typing import ClassVar as _ClassVar, Optional as _Optional
from pathlib import Path as _Path


__all__ = ("TPStack", "FileManager")


class TPStack:
    """Стек для управления ресурсами TurboPrint."""
    
    _stack: _ClassVar[list["TPStack"]] = []
    
    def __init__(self) -> None:
        """Инициализация стека."""
        self._stack.append(self)
    
    @classmethod
    def clear(cls) -> None:
        """Очистить все ресурсы из стека."""
        cls._stack.clear()
    
    @classmethod
    def close(cls) -> None:
        """Закрыть и очистить все ресурсы из стека."""
        cls.clear()


class FileManager:
    """Менеджер для операций с файлами."""
    
    def __init__(self, path: _Optional[_Path] = None) -> None:
        """Инициализация менеджера файлов.
        
        Аргументы:
            path: Необязательный путь для управления. Если не указан, будет использован путь по умолчанию.
        """
        self._path = path or _Path.cwd()


_register_atexit(TPStack.close)
