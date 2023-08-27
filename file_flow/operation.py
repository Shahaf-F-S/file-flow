# operation.py

import datetime as dt
from typing import TypeVar, Generic, Optional, Callable

from attrs import define

from file_flow.process import ProcessTime, ProcessResponse

__all__ = [
    "OperationResponse",
    "Operator"
]

_D = TypeVar("_D")
_O = TypeVar("_O")

@define
class OperationResponse(ProcessResponse[_D, _O]):
    """A class to represent a response object for an operation of a file."""
# end OperationResponse

class Operator(Generic[_D, _O]):
    """A class to represent a """

    def __init__(self, command: Optional[Callable[[_D], _O]] = None) -> None:
        """
        Defines the command of the operator.

        :param command: The default command to run.
        """

        self.command = command
    # end __init__

    def __call__(self, data: _D) -> OperationResponse[_D, _O]:
        """
        Executes the operation on the source file.

        :param data: The source data of the file to operate on.

        :return: The response object.
        """

        return self.execute(data=data)
    # end __call__

    def before(self, data: _D) -> None:
        """
        Executes the operation on the source file.

        :param data: The source data of the file to operate on.

        :return: Any return value.
        """
    # end before

    def after(self, data: _O) -> None:
        """
        Executes the operation on the source file.

        :param data: The source data of the file to operate on.

        :return: Any return value.
        """
    # end after

    def operation(self, data: _D) -> _O:
        """
        Executes the operation on the source file.

        :param data: The source data of the file to operate on.

        :return: Any return value.
        """

        if self.command is None:
            return data

        else:
            return self.command(data)
        # end if
    # end operation

    def execute(self, data: _D) -> OperationResponse[_D, _O]:
        """
        Executes the operation on the source file.

        :param data: The source data of the file to operate on.

        :return: The response object.
        """

        start = dt.datetime.now()

        self.before(data)

        results = self.operation(data=data)

        self.after(results)

        end = dt.datetime.now()

        return OperationResponse[_D, _O](
            caller=self,
            time=ProcessTime(start=start, end=end),
            data=data,
            output=results
        )
    # end execute
# end Operator