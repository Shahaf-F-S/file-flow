# process.py

import datetime as dt
from uuid import uuid4
from typing import Generic, TypeVar, Any

from attrs import define

__all__ = [
    "ProcessTime",
    "ProcessResponse"
]

@define
class ProcessTime:
    """A class to represent the start, end and total time for a process to finish."""

    start: dt.datetime
    end: dt.datetime

    @property
    def time(self) -> dt.timedelta:
        """
        Returns the amount of the process took to finish.

        :return: The timedelta object of time duration.
        """

        return self.end - self.start

_D = TypeVar("_D")
_O = TypeVar("_O")

@define
class ProcessResponse(Generic[_D, _O]):
    """A class to represent a response object for an operation of a file."""

    data: _D
    output: _O
    time: ProcessTime
    process_id: str = None
    caller: Any = None

    def __attrs_post_init__(self) -> None:
        """Defines the attributes after initialization."""

        self.process_id = self.process_id or str(uuid4())
