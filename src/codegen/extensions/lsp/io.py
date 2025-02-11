import logging
from pathlib import Path

from lsprotocol.types import TextDocumentContentChangeWholeDocument
from pygls.workspace import TextDocument, Workspace

from codegen.sdk.codebase.io.file_io import FileIO
from codegen.sdk.codebase.io.io import IO

logger = logging.getLogger(__name__)


class LSPIO(IO):
    base_io: FileIO
    workspace: Workspace

    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.base_io = FileIO()

    def _get_doc(self, path: Path) -> TextDocument | None:
        uri = path.as_uri()
        logger.info(f"Getting document for {uri}")
        return self.workspace.get_text_document(uri)

    def read_text(self, path: Path) -> str:
        if doc := self._get_doc(path):
            return doc.source
        return self.base_io.read_text(path)

    def read_bytes(self, path: Path) -> bytes:
        if doc := self._get_doc(path):
            return doc.source.encode("utf-8")
        return self.base_io.read_bytes(path)

    def write_bytes(self, path: Path, content: bytes) -> None:
        change = TextDocumentContentChangeWholeDocument(
            text=content.decode("utf-8"),
        )
        if doc := self._get_doc(path):
            doc.apply_change(change)
        else:
            self.base_io.write_bytes(path, content)

    def save_files(self, files: set[Path] | None = None) -> None:
        self.base_io.save_files(files)

    def check_changes(self) -> None:
        self.base_io.check_changes()

    def delete_file(self, path: Path) -> None:
        self.base_io.delete_file(path)

    def file_exists(self, path: Path) -> bool:
        if doc := self._get_doc(path):
            try:
                doc.source
            except FileNotFoundError:
                return False
            return True
        return self.base_io.file_exists(path)

    def untrack_file(self, path: Path) -> None:
        self.base_io.untrack_file(path)
