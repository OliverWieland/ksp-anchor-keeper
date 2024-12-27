import time
from queue import Queue
from threading import Timer
from typing import Union

from watchdog.events import (
    DirCreatedEvent,
    DirModifiedEvent,
    FileCreatedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
)


class SfsFileHandler(FileSystemEventHandler):
    def __init__(self, file_queue: Queue[str], debounce_interval: float = 1.0) -> None:
        self.queue = file_queue
        self.debounce_interval = debounce_interval
        self.last_modified_time: dict[str, float] = {}
        self.debounce_timers: dict[str, Timer] = {}
        self.sfs_files: set[str] = set()

    def _process_file(self, src_path: str):
        """This method is called to process the last event."""
        self.queue.put(src_path)

    def _reset_timer(self, src_path: str):
        """Reset the timer for the specific file."""
        if src_path in self.debounce_timers:
            self.debounce_timers[src_path].cancel()

        timer = Timer(self.debounce_interval, self._process_file, args=(src_path,))
        self.debounce_timers[src_path] = timer
        timer.start()

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        src_path = str(event.src_path)

        if src_path.endswith(".sfs"):
            self.sfs_files.add(src_path)

            # Update the timer for this specific file
            self.last_modified_time[src_path] = time.time()
            self._reset_timer(src_path)

    def on_modified(self, event: Union[DirModifiedEvent, FileModifiedEvent]) -> None:
        src_path = str(event.src_path)

        if src_path.endswith(".sfs"):
            self.sfs_files.add(src_path)

            # Update the timer for this specific file
            self.last_modified_time[src_path] = time.time()
            self._reset_timer(src_path)
