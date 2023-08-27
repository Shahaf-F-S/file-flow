# io.py

from typing import (
    TypeVar, Generic, ClassVar,
    Optional, Callable, Type, Any, Dict
)

from attrs import define

__all__ = [
    "IO",
    "TextIO",
    "BytesIO",
    "IOContainer"
]

_D = TypeVar("_D")

@define
class IO(Generic[_D]):
    """A class to represent a generic io operation handler."""

    loader: Optional[Callable[[str], _D]] = None
    saver: Optional[Callable[[_D, str], None]] = None

    name: ClassVar[str] = None
    silent: Optional[bool] = None

    load_kwargs: Optional[Dict[str, Any]] = None
    save_kwargs: Optional[Dict[str, Any]] = None

    base: ClassVar[Type] = _D

    def load(self, path: str, **kwargs: Any) -> _D:
        """
        Loads the data from the file.

        :param path: The path to the source file.

        :return: The loaded file data.
        """

        if self.loader is not None:
            return self.loader(path)
        # end if
    # end load

    def save(self, data: _D, path: str, **kwargs: Any) -> None:
        """
        Loads the data from the file.

        :param path: The path to save the data.
        :param data: The data to save in the file.
        """

        if self.saver is not None:
            self.saver(data, path)
        # end if
    # end load
# end ID

@define
class TextIO(IO[str]):
    """A class to represent a text io operation handler."""

    name: ClassVar[str] = "txt"
    base: ClassVar[Type[str]] = str

    def load(self, path: str, **kwargs: Any) -> str:
        """
        Loads the data from the file.

        :param path: The path to the source file.

        :return: The loaded file data.
        """

        with open(path, "r") as file:
            return file.read()
        # end open
    # end load

    def save(self, data: str, path: str, **kwargs: Any) -> None:
        """
        Loads the data from the file.

        :param path: The path to save the data.
        :param data: The data to save in the file.
        """

        with open(path, "w") as file:
            file.write(data)
        # end open
    # end load
# end TextIO

@define
class BytesIO(IO[bytes]):
    """A class to represent a bytes io operation handler."""

    name: ClassVar[str] = "bytes"
    base: ClassVar[Type[bytes]] = bytes

    def load(self, path: str, **kwargs: Any) -> bytes:
        """
        Loads the data from the file.

        :param path: The path to the source file.

        :return: The loaded file data.
        """

        with open(path, "rb") as file:
            return file.read()
        # end open
    # end load

    def save(self, data: bytes, path: str, **kwargs: Any) -> None:
        """
        Loads the data from the file.

        :param path: The path to save the data.
        :param data: The data to save in the file.
        """

        with open(path, "wb") as file:
            file.write(data)
        # end open
    # end load
# end BytesIO

_O = TypeVar("_O")

@define
class IOContainer(Generic[_D, _O]):
    """A class to contain io objects."""

    input: Optional[IO[_D]] = None
    output: Optional[IO[_O]] = None
# end IOContainer