import logging
from pathlib import Path

from lsprotocol import types
from lsprotocol.types import Position, Range, TextEdit
from pygls.workspace import TextDocument, Workspace

from codegen.sdk.codebase.io.file_io import FileIO
from codegen.sdk.codebase.io.io import IO

logger = logging.getLogger(__name__)


class LSPIO(IO):
    base_io: FileIO
    workspace: Workspace
    changes: dict[str, TextEdit] = {}

    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.base_io = FileIO()

    def _get_doc(self, path: Path) -> TextDocument | None:
        uri = path.as_uri()
        logger.info(f"Getting document for {uri}")
        return self.workspace.get_text_document(uri)

    def read_bytes(self, path: Path) -> bytes:
        if self.changes.get(path.as_uri()):
            return self.changes[path.as_uri()].new_text.encode("utf-8")
        if doc := self._get_doc(path):
            return doc.source.encode("utf-8")
        return self.base_io.read_bytes(path)

    def write_bytes(self, path: Path, content: bytes) -> None:
        logger.info(f"Writing bytes to {path}")
        start = Position(line=0, character=0)
        if doc := self._get_doc(path):
            end = Position(line=len(doc.source), character=len(doc.source))
        else:
            end = Position(line=0, character=0)
        self.changes[path.as_uri()] = TextEdit(range=Range(start=start, end=end), new_text=content.decode("utf-8"))

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

    def get_document_changes(self) -> list[types.TextDocumentEdit]:
        ret = []
        for uri, change in self.changes.items():
            id = types.OptionalVersionedTextDocumentIdentifier(uri=uri)
            ret.append(types.TextDocumentEdit(text_document=id, edits=[change]))
        self.changes = {}
        return ret
