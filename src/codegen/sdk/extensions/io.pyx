from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import os


def write_file(file_path: Path, content: bytes):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)


def write_changes(files_to_remove: list[Path], files_to_write: list[tuple[Path, bytes]]):
    # Start at the oldest sync and then apply non-conflicting newer changes
    with ThreadPoolExecutor() as executor:
        for file_to_remove in files_to_remove:
            executor.submit(os.remove, file_to_remove)
        for file_to_write, content in files_to_write:
            executor.submit(write_file, file_to_write, content)
