from abc import ABC, abstractmethod
from pathlib import Path


class BadWriteError(Exception):
    pass


class IO(ABC):
    def write_text(self, path: Path, content: str) -> None:
        self.write_bytes(path, content.encode("utf-8"))

    @abstractmethod
    def untrack_file(self, path: Path) -> None:
        pass

    @abstractmethod
    def write_bytes(self, path: Path, content: bytes) -> None:
        pass

    @abstractmethod
    def read_bytes(self, path: Path) -> bytes:
        pass

    @abstractmethod
    def save_file(self, path: Path) -> None:
        pass

    @abstractmethod
    def check_changes(self) -> None:
        pass

    @abstractmethod
    def delete_file(self, path: Path) -> None:
        pass
