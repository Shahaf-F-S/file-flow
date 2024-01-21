# test.py

from file_flow.events import FileSystemEvent
from file_flow.io import TextIO, IOContainer
from file_flow.pipeline import Pipeline
from file_flow.operation import Operator
from file_flow.watcher import Watcher
from file_flow.handler import PatternHandler

def main() -> None:
    """Tests the main functionalities of the program."""

    handler = PatternHandler(
        patterns={"*.txt": IOContainer(TextIO(), TextIO())},
        pipelines={FileSystemEvent: [Pipeline([Operator(lambda data: print(data))])]}
    )

    watcher = Watcher(root="demo", handler=handler)

    watcher.run()

if __name__ == '__main__':
    main()
