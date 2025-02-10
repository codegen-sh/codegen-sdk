import logging
from pathlib import Path

from codegen.sdk.codebase.io.io import IO, BadWriteError

logger = logging.getLogger(__name__)


class FileIO(IO):
    files: dict[Path, bytes]

    def __init__(self):
        self.files = {}

    def write_bytes(self, path: Path, content: bytes) -> None:
        self.files[path] = content

    def read_bytes(self, path: Path) -> bytes:
        if path not in self.files:
            self.files[path] = path.read_bytes()
        return self.files[path]

    def save_file(self, path: Path) -> None:
        path.write_bytes(self.files[path])
        del self.files[path]

    def check_changes(self) -> None:
        if self.files:
            logger.error(BadWriteError("Directly called file write without calling commit_transactions"))

    def delete_file(self, path: Path) -> None:
        del self.files[path]
        path.unlink()

    def untrack_file(self, path: Path) -> None:
        del self.files[path]
