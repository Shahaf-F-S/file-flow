# handler.py

import os
from uuid import uuid4
from pathlib import Path
import threading
from typing import Iterable, TypeVar, Generic, Any
from pathlib import PurePosixPath, PureWindowsPath

from attrs import define

from watchdog.events import (
    PatternMatchingEventHandler, FileSystemEvent
)

from file_flow.pipeline import Pipeline, PipelineResponse
from file_flow.data_io import IOContainer

__all__ = [
    "match_path",
    "PatternHandler",
    "HandlingResponse",
    "relocation_path"
]

def relocation_path(path: str, source: str, destination: str) -> str:
    """
    Finds the path in witch the file should be after replacing the source with the destination.

    :param path: The path to the file.
    :param source: The source location.
    :param destination: The destination location.

    :return: The new file path.
    """

    return (
        str(Path(path).absolute()).replace(
            str(Path(source).absolute()),
            str(Path(destination).absolute())
        )
    )

def match_path(
        path: str,
        included_patterns: Iterable[str],
        excluded_patterns: Iterable[str],
        case_sensitive: bool = False
) -> bool:
    """
    Checks if a path is matching the validation and invalidation patterns.

    :param path: The file path to check.
    :param included_patterns: The patterns to return true.
    :param excluded_patterns: The patterns to return false.
    :param case_sensitive: The value to check case sensitivity.

    :return: The match value.
    """

    if case_sensitive:
        path = PurePosixPath(path)

    else:
        included_patterns = {pattern.lower() for pattern in included_patterns}
        excluded_patterns = {pattern.lower() for pattern in excluded_patterns}

        path = PureWindowsPath(path)

    common_patterns = included_patterns & excluded_patterns
    if common_patterns:
        raise ValueError(
            f"conflicting patterns '{common_patterns}' included and excluded."
        )

    return (
        any(path.match(p) for p in included_patterns) and
        not any(path.match(p) for p in excluded_patterns)
    )

_D = TypeVar("_D")
_O = TypeVar("_O")

@define
class HandlingResponse(Generic[_D, _O]):
    """A class to represent the response from the handling process."""

    pattern: str
    io: IOContainer[_D, _O]
    event: FileSystemEvent
    data: _D
    output: dict[type[FileSystemEvent], list[PipelineResponse[_D, _O]]]

    process_id: str = None
    caller: Any = None
    destination: str = None

    def __attrs_post_init__(self) -> None:
        """Defines the attributes after initialization."""

        self.process_id = self.process_id or str(uuid4())

    @property
    def source(self) -> str:
        """
        The source location of the files to listen to.

        :return: The source path.
        """

        return str(Path(self.event.src_path))
    # ene source

    @property
    def result(self) -> _O:
        """
        Returns the result video object.

        :return: The video object.
        """

        try:
            return list(self.output.items())[0][1][-1].output[-1].output

        except IndexError:
            raise ValueError("No result value due to no operations.")

    def has_result(self) -> bool:
        """
        Checks if there is a result object.

        :return: The validation value.
        """

        try:
            dir(self.result)

            return True

        except ValueError:
            return False

Pipelines = dict[type[FileSystemEvent], Iterable[Pipeline]]
Patterns = dict[str, IOContainer]
Events = Iterable[type[FileSystemEvent]]
Results = dict[type[FileSystemEvent], list[PipelineResponse[_D, _O]]]

class PatternHandler(Generic[_D, _O], PatternMatchingEventHandler):
    """A class to represent a handler of file events."""

    IGNORE_DIRECTORIES = False
    CASE_SENSITIVE = False

    PIPELINES: Pipelines = None
    PATTERNS: Patterns = None
    IGNORED: Events = None

    DESTINATION: str = None

    RESPONSE_TYPE = HandlingResponse[_D, _O]

    def __init__(
            self,
            pipelines: Pipelines = None,
            patterns: Patterns = None,
            ignored: Events = None,
            ignore_directories: bool = None,
            case_sensitive: bool = None,
            destination: str = None
    ) -> None:
        """
        Defines the attributes for the file events handling.

        :param pipelines: The pipelines to run.
        :param patterns: The patterns to match with the files.
        :param ignored: The types of events to ignore.
        :param ignore_directories: The value to exclude directories.
        :param case_sensitive: The value for case sensitivity.
        :param destination: The saving destination for all files.
        """

        if ignore_directories is None:
            ignore_directories = self.IGNORE_DIRECTORIES

        if case_sensitive is None:
            case_sensitive = self.CASE_SENSITIVE

        if pipelines is None:
            pipelines = self.PIPELINES

        if patterns is None:
            patterns = self.PATTERNS

        if ignored is None:
            ignored = self.IGNORED

        if destination is None:
            destination = self.DESTINATION

        if None in (patterns, pipelines):
            raise ValueError(
                "patterns and pipelines must be defined, "
                "either by class or by instance."
            )

        self.pipelines = pipelines

        self.patterns_io = patterns

        self.destination = destination

        PatternMatchingEventHandler.__init__(
            self,
            patterns=list(patterns.keys()),
            ignore_directories=ignore_directories,
            case_sensitive=case_sensitive
        )

        self.handled: list[tuple[str, str, bool]] = []
        self.responses: list[HandlingResponse[_D, _O]] = []

        self.ignored: list[type[FileSystemEvent]] = list(ignored or [])

        self.saving = True

    def is_mach(self, path: str, pattern: str) -> bool:
        """
        Checks if a path is matching the validation and invalidation patterns.

        :param path: The file path to check.
        :param pattern: The pattern to match

        :return: The match value.
        """

        return match_path(
            path=path,
            included_patterns=[pattern],
            excluded_patterns=[],
            case_sensitive=self.case_sensitive
        )

    def is_valid_event(self, event: FileSystemEvent) -> bool:
        """
        Checks if the event should be processed.

        :param event: The file system event to handle.

        :return: The validation value.
        """

        for base in self.ignored:
            if isinstance(event, base):
                return False

        for base in self.pipelines:
            if isinstance(event, base):
                return True

        return False

    def get_event_match(self, event: FileSystemEvent) -> tuple[str, IOContainer] | None:

        for pattern, io_container in self.patterns_io.items():
            if self.is_mach(path=event.src_path, pattern=pattern):
                return pattern, io_container

        else:
            return

    def is_registered(self, event: FileSystemEvent) -> bool:
        """
        Checks if the event is registered.

        :param event: The event to check.

        :return: The validation value.
        """

        return event.key in self.handled

    def register_event(self, event: FileSystemEvent) -> None:
        """
        Registers the event.

        :param event: The file system event to handle.
        """

        self.handled.append(event.key)

    def unregister_event(self, event: FileSystemEvent) -> None:
        """
        Unregisters the event.

        :param event: The file system event to handle.
        """

        self.handled.remove(event.key)

    def before(
            self, pattern: str, io: IOContainer, event: FileSystemEvent
    ) -> None:
        """
        A callback to run before executing the process of the event.

        :param pattern: The pattern that detected the file.
        :param io: The io object for data I/O.
        :param event: The file system event to handle.
        """

    def after(
            self, pattern: str, io: IOContainer, event: FileSystemEvent
    ) -> None:
        """
        A callback to run after executing the process of the event.

        :param pattern: The pattern that detected the file.
        :param io: The io object for data I/O.
        :param event: The file system event to handle.
        """

    def load(
            self,
            io: IOContainer,
            event: FileSystemEvent,
            path: str | Path = None
    ) -> _D:
        """
        Loads the data from the path generated with the event, using the IO object.

        :param io: The io object for data I/O.
        :param event: The file system event to handle.
        :param path: The path to the file to load.

        :return: The loaded data object.
        """

        dir(event)
        dir(self)

        if path is None:
            path = event.src_path

        return io.input.load(path=path)

    def before_load(
            self,
            io: IOContainer,
            event: FileSystemEvent,
            path: str | Path
    ) -> None:
        """
        A callback to run before saving the result.

        :param io: The io object for data I/O.
        :param event: The file system event to handle.
        :param path: The path to the file to load.
        """

    def after_load(
            self,
            io: IOContainer,
            event: FileSystemEvent,
            path: str | Path,
            data: _D
    ) -> None:
        """
        A callback to run before saving the result.

        :param io: The io object for data I/O.
        :param event: The file system event to handle.
        :param path: The path to the file to load.
        :param data: The loaded data.
        """

    def saving_path(
            self,
            response: HandlingResponse,
            path: str | Path = None
    ) -> str:
        """
        Generates a new saving path for the data.

        :param response: The response object.
        :param path: The path to the file to load.

        :return: The saving path.
        """

        dir(response)
        dir(self)

        if path is None:
            path = response.destination

        if path is None:
            location, file = os.path.split(response.source)

            if self.destination is None:
                path = str(Path(location) / Path(f"output_{file}"))

            else:
                path = relocation_path(
                    path=response.source, source=location,
                    destination=self.destination
                )

        return path

    def save(
            self,
            response: HandlingResponse,
            path: str | Path = None
    ) -> str:
        """
        Saves the data to the path generated with the event, using the IO object.

        :param response: The response object.
        :param path: The path to the file to load.

        :return: The saving path.
        """

        dir(self)

        if path is None:
            path = response.destination

        if path is None:
            path = self.saving_path(response=response, path=path)

        response.io.output.save(data=response.result, path=path)

        return str(path)

    def before_save(self, response: HandlingResponse, path: str) -> None:
        """
        A callback to run before saving the result.

        :param response: The response object.
        :param path: The path to the file to load.
        """

    def after_save(self, response: HandlingResponse, path: str) -> None:
        """
        A callback to run before saving the result.

        :param response: The response object.
        :param path: The path to the file to load.
        """

    def execute(self, data: _D, event: FileSystemEvent) -> Results:
        """
        Executes the processes of the pipelines on the data from the event.

        :param data: The data to feed the execution.
        :param event: The source event of the data.

        :return: The returned values from the processes.
        """

        results: Results = {}

        for base, pipelines in self.pipelines.items():
            if isinstance(event, base):
                for pipeline in pipelines:
                    results.setdefault(base, []).append(
                        pipeline.execute(data=data)
                    )

        return results

    def create_response(
            self,
            pattern: str,
            io: IOContainer,
            data: _D,
            event: FileSystemEvent,
            results: Results
    ) -> HandlingResponse[_D, _O]:
        """
        Executes the processes of the pipelines on the data from the event.

        :param data: The data to feed the execution.
        :param event: The source event of the data.
        :param pattern: The pattern that detected the file.
        :param io: The io object for data I/O.
        :param results: The results of the process.

        :return: The returned values from the processes.
        """

        return self.RESPONSE_TYPE(
            caller=self, data=data, pattern=pattern,
            io=io, event=event, output=results
        )

    def response(
            self,
            pattern: str,
            io: IOContainer,
            data: _D,
            event: FileSystemEvent,
            results: Results
    ) -> HandlingResponse[_D, _O]:
        """
        Executes the processes of the pipelines on the data from the event.

        :param data: The data to feed the execution.
        :param event: The source event of the data.
        :param pattern: The pattern that detected the file.
        :param io: The io object for data I/O.
        :param results: The results of the process.

        :return: The returned values from the processes.
        """

        response = self.create_response(
            data=data, pattern=pattern,
            io=io, event=event, results=results
        )

        return self.process_response(response=response)

    def process_response(
            self, response: HandlingResponse[_D, _O]
    ) -> HandlingResponse[_D, _O]:
        """
        Executes a specific pipeline for each event.

        :param response: The response to handle and return.

        :return: The handling response object, if there is one.
        """

        dir(self)

        return response

    def is_savable(self, response: HandlingResponse[_D, _O]) -> bool:
        """
        Checks if the data is savable.

        :param response: The response to handle and return.

        :return: The validation value.
        """

        dir(self)

        return response.io.output is not None

    def process(
            self, pattern: str, io: IOContainer, event: FileSystemEvent
    ) -> HandlingResponse[_D, _O]:
        """
        Executes a specific pipeline for each event.

        :param pattern: The pattern that detected the file.
        :param io: The io object for data I/O.
        :param event: The file system event to handle.

        :return: The handling response object, if there is one.
        """

        self.before(pattern=pattern, io=io, event=event)

        source = str(Path(event.src_path))

        self.before_load(io=io, path=source, event=event)
        data = self.load(io=io, path=source, event=event)
        self.after_load(io=io, path=source, event=event, data=data)

        results = self.execute(data=data, event=event)

        response = self.response(
            data=data, pattern=pattern,
            io=io, event=event, results=results
        )

        if self.saving and self.is_savable(response=response):
            destination = self.saving_path(response=response)

            response.destination = destination

            self.before_save(response=response, path=destination)

            response.destination = self.save(response=response, path=destination)

            self.after_save(response=response, path=destination)

        self.after(pattern=pattern, io=io, event=event)

        return response

    def handle(self, event: FileSystemEvent) -> None:
        """
        Executes a specific pipeline for each event.

        :param event: The file system event to handle.
        """

        if (
            self.is_valid_event(event) and
            (not self.register_event(event)) and
            (match := self.get_event_match(event))
        ):
            self.register_event(event)

            pattern, io_container = match

            threading.Thread(
                target=lambda: (
                    self.responses.append(
                        self.process(
                            pattern=pattern, io=io_container,
                            event=event
                        )
                    )
                )
            ).start()

    def on_any_event(self, event: FileSystemEvent) -> None:
        """
        Executes a specific pipeline for each event.

        :param event: The file system event to handle.
        """

        self.handle(event=event)
