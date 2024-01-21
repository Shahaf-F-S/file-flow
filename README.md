# project-template

> An event system for file operations to execute commands for file events.

## Installation

```
pip install auto-file-flow
```

## example

```python
from file_flow.events import FileSystemEvent
from file_flow.io import TextIO, IOContainer
from file_flow.pipeline import Pipeline
from file_flow.operation import Operator
from file_flow.watcher import Watcher
from file_flow.handler import PatternHandler

handler = PatternHandler(
  patterns={"*.txt": IOContainer(TextIO(), TextIO())},
  pipelines={FileSystemEvent: [Pipeline([Operator(lambda data: print(data))])]}
)

watcher = Watcher(root="demo", handler=handler)

watcher.run()
```