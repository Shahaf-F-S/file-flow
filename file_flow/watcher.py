# watcher.py

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

__all__ = [
    "Watcher"
]

class Watcher:
    """A class to represent a controller of handler objects."""

    def __init__(self, root: str, handler: FileSystemEventHandler) -> None:

        self.root = root

        self.handler = handler

        self.observer = Observer()

    def watch(self) -> None:
        """Handles the runtime of the loop."""

    def run(self) -> None:
        """Runs the loop handling."""

        self.observer.schedule(self.handler, self.root, recursive=True)
        self.observer.start()

        while True:
            self.watch()

    def stop(self) -> None:
        """Stops the running process, if there is one."""

        self.observer.stop()
        self.observer.join()
