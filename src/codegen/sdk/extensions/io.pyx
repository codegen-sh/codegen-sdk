from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import os


def write_changes(files_to_remove: list[Path], files_to_write: list[tuple[Path, bytes]]):
    # Start at the oldest sync and then apply non-conflicting newer changes
    with ThreadPoolExecutor() as executor:
        for file_to_remove in files_to_remove:
            executor.submit(os.remove, file_to_remove)
        for file_to_write, content in files_to_write:
            executor.submit(file_to_write.write_bytes, content)
