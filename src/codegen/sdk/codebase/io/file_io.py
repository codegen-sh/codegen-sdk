import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from codegen.sdk.codebase.io.io import IO, BadWriteError

logger = logging.getLogger(__name__)


class FileIO(IO):
    """IO implementation that writes files to disk, and tracks pending changes."""

    files: dict[Path, bytes]

    def __init__(self):
        self.files = {}

    def write_bytes(self, path: Path, content: bytes) -> None:
        self.files[path] = content

    def read_bytes(self, path: Path) -> bytes:
        if path not in self.files:
            self.files[path] = path.read_bytes()
        return self.files[path]

    def save_files(self, files: set[Path] | None = None) -> None:
        to_save = set(filter(lambda f: f in files, self.files)) if files is not None else self.files
        with ThreadPoolExecutor() as exec:
            exec.map(lambda path: path.write_bytes(self.files[path]), to_save)
        for path in to_save:
            del self.files[path]

    def check_changes(self) -> None:
        if self.files:
            logger.error(BadWriteError("Directly called file write without calling commit_transactions"))
        self.files.clear()

    def delete_file(self, path: Path) -> None:
        del self.files[path]
        path.unlink()

    def untrack_file(self, path: Path) -> None:
        del self.files[path]

    def file_exists(self, path: Path) -> bool:
        return path.exists()
