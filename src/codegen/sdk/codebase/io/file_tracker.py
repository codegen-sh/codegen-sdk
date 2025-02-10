from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from codegen.sdk.codebase.io.file_io import FileIO
from codegen.sdk.codebase.io.io import IO


class FileTracker:
    pending_files: set[Path]
    io: IO

    def __init__(self, io: IO | None = None):
        self.pending_files = set()
        if io is None:
            io = FileIO()
        self.io = io

    def write_file(self, path: Path, content: str | bytes | None) -> None:
        if content is not None:
            self.pending_files.add(path)
        if isinstance(content, str):
            self.io.write_text(path, content)
        elif isinstance(content, bytes):
            self.io.write_bytes(path, content)
        else:
            self.io.untrack_file(path)

    def save_files(self, files: set[Path] | None = None) -> None:
        to_save = set(filter(lambda f: f in files, self.pending_files)) if files is not None else self.pending_files
        with ThreadPoolExecutor() as exec:
            exec.map(lambda f: self.io.save_file(f), to_save)
        self.pending_files.difference_update(to_save)

    def check_changes(self) -> None:
        self.io.check_changes()
        self.pending_files.clear()

    def read_bytes(self, path: Path) -> bytes:
        return self.io.read_bytes(path)

    def delete_file(self, path: Path) -> None:
        self.io.delete_file(path)
