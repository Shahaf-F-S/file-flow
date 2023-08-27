# pipeline.py

import datetime as dt
from typing import Iterable, List, Optional, TypeVar, Generic

from attrs import define

from file_flow.operation import Operator, OperationResponse
from file_flow.process import ProcessResponse, ProcessTime

_D = TypeVar("_D")
_O = TypeVar("_O")

@define
class PipelineResponse(ProcessResponse[_D, List[OperationResponse[_D, _O]]]):
    """A class to represent a response object for an operation of a file."""
# end PipelineResponse

class Pipeline(Generic[_D, _O]):
    """A class to represent a pipeline of file operations."""

    def __init__(self, operators: Optional[Iterable[Operator]] = None) -> None:
        """
        Defines the pipeline attributes.

        :param operators: The operations to execute sequentially on the source file.
        """

        self.operators = list(operators or [])
    # end __init__

    def execute(self, data: _D) -> PipelineResponse:
        """
        Executes the chain of operations of the file.

        :param data: The source data of the file to operate on.

        :return: The list of responses for all the operations.
        """

        source = data

        start = dt.datetime.now()

        responses: List[OperationResponse] = []

        for operation in self.operators:
            response = operation(data)

            data = response.output

            responses.append(response)
        # end for

        end = dt.datetime.now()

        return PipelineResponse(
            caller=self,
            time=ProcessTime(start=start, end=end),
            data=source,
            output=responses
        )
    # end execute
# end Pipeline