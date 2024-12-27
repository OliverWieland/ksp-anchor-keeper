import time
from pathlib import Path
from queue import Queue
from typing import Any

import sfsutils
from watchdog.observers import Observer

import database
from config import Config
from filehandler import SfsFileHandler
from groundanchor import (
    GroundAnchor,
    extract_anchors,
    inspect_anchors,
    merge_anchors,
    restore_anchor,
)


def process_savefile(
    path: str, cached_anchors: set[GroundAnchor], db_path: Path
) -> None:
    savefile: dict[str, Any] = sfsutils.parse_savefile(path)  # type: ignore
    current_anchors = extract_anchors(savefile)  # type: ignore
    anchors = merge_anchors(current_anchors, cached_anchors)
    anchors_to_restore = inspect_anchors(anchors, cached_anchors)
    database.save_to_sqlite(db_path, cached_anchors)

    if anchors_to_restore:
        for anchor in anchors_to_restore:
            print(f"Restoring Stamp-O-Tron Ground Anchor {anchor.pid}")
            savefile = restore_anchor(savefile, anchor)  # type: ignore

        sfsutils.writeout_savefile(savefile, path)  # type: ignore


def main():
    # Load configuration
    config = Config()

    # Load cached anchors from configured database path
    cached_anchors: set[GroundAnchor] = database.load_from_sqlite(
        str(config.database_path)
    )

    file_queue: Queue[str] = Queue()

    event_handler = SfsFileHandler(file_queue)
    observer = Observer()
    observer.schedule(event_handler, path=str(config.saves_directory), recursive=False)
    observer.start()

    try:
        print(
            f"Monitoring .sfs files in directory {config.saves_directory}. Press Ctrl+C to exit."
        )
        while True:
            if not file_queue.empty():
                path = file_queue.get()
                process_savefile(path, cached_anchors, config.database_path)
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
