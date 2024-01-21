# io.py

from typing import (
    TypeVar, Generic, ClassVar, Callable, Any
)
from dataclasses import dataclass

__all__ = [
    "IO",
    "TextIO",
    "BytesIO",
    "IOContainer"
]

_D = TypeVar("_D")

@dataclass
class IO(Generic[_D]):
    """A class to represent a generic io operation handler."""

    loader: Callable[[str], _D] = None
    saver: Callable[[_D, str], Any] = None

    name: ClassVar[str] = None
    silent: bool = None

    load_kwargs: dict[str, Any] = None
    save_kwargs: dict[str, Any] = None

    base: ClassVar[type] = _D

    def load(self, path: str, **kwargs: Any) -> _D:
        """
        Loads the data from the file.

        :param path: The path to the source file.

        :return: The loaded file data.
        """

        if self.loader is not None:
            return self.loader(path)

    def save(self, data: _D, path: str, **kwargs: Any) -> None:
        """
        Loads the data from the file.

        :param path: The path to save the data.
        :param data: The data to save in the file.
        """

        if self.saver is not None:
            self.saver(data, path)

@dataclass
class TextIO(IO[str]):
    """A class to represent a text io operation handler."""

    name: ClassVar[str] = "txt"
    base: ClassVar[type[str]] = str

    def load(self, path: str, **kwargs: Any) -> str:
        """
        Loads the data from the file.

        :param path: The path to the source file.

        :return: The loaded file data.
        """

        with open(path, "r") as file:
            return file.read()

    def save(self, data: str, path: str, **kwargs: Any) -> None:
        """
        Loads the data from the file.

        :param path: The path to save the data.
        :param data: The data to save in the file.
        """

        with open(path, "w") as file:
            file.write(data)

@dataclass
class BytesIO(IO[bytes]):
    """A class to represent a bytes io operation handler."""

    name: ClassVar[str] = "bytes"
    base: ClassVar[type[bytes]] = bytes

    def load(self, path: str, **kwargs: Any) -> bytes:
        """
        Loads the data from the file.

        :param path: The path to the source file.

        :return: The loaded file data.
        """

        with open(path, "rb") as file:
            return file.read()

    def save(self, data: bytes, path: str, **kwargs: Any) -> None:
        """
        Loads the data from the file.

        :param path: The path to save the data.
        :param data: The data to save in the file.
        """

        with open(path, "wb") as file:
            file.write(data)

_O = TypeVar("_O")

@dataclass
class IOContainer(Generic[_D, _O]):
    """A class to contain io objects."""

    input: IO[_D] = None
    output: IO[_D] = None
