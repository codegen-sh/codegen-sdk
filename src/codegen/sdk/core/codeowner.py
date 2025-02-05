import logging
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Callable, Literal, TypeVar

from codeowners import CodeOwners as CodeOwnersParser

from codegen.git.utils.cache_utils import cached_generator
from codegen.sdk.core.interfaces.files_interface import FilesInterface, FilesParam, TFile
from codegen.shared.decorators.docs import apidoc

if TYPE_CHECKING:
    from codegen.sdk.core.symbol import Symbol

logger = logging.getLogger(__name__)


TSymbol = TypeVar("TSymbol", bound="Symbol")


@apidoc
class CodeOwner(FilesInterface):
    """CodeOwner is a class that represents a code owner in a codebase.

    It is used to iterate over all files that are owned by a specific owner.

    Attributes:
        owner_type: The type of the owner (USERNAME, TEAM, EMAIL).
        owner_value: The value of the owner.
        files_source: A callable that returns an iterable of all files in the codebase.
    """

    owner_type: Literal["USERNAME", "TEAM", "EMAIL"]
    owner_value: str
    files_source: Callable[FilesParam, Iterable[TFile]]

    def __init__(self, files_source: Callable[FilesParam, Iterable[TFile]], owner_type: Literal["USERNAME", "TEAM", "EMAIL"], owner_value: str):
        self.owner_type = owner_type
        self.owner_value = owner_value
        self.files_source = files_source
        self.files = self.files_generator

    @classmethod
    def from_parser(cls, parser: CodeOwnersParser, file_source: Callable[FilesParam, Iterable[TFile]]) -> list["CodeOwner"]:
        """Create a list of CodeOwner objects from a CodeOwnersParser.

        Args:
            parser (CodeOwnersParser): The CodeOwnersParser to use.
            file_source (Callable[FilesParam, Iterable[TFile]]): A callable that returns an iterable of all files in the codebase.

        Returns:
            list[CodeOwner]: A list of CodeOwner objects.
        """
        codeowners = []
        for _, _, owners, _, _ in parser.paths:
            for owner_label, owner_value in owners:
                codeowners.append(CodeOwner(file_source, owner_label, owner_value))
        return codeowners

    @cached_generator(maxsize=16)
    def files_generator(self, *args: FilesParam.args, **kwargs: FilesParam.kwargs) -> Iterable[TFile]:
        for source_file in self.files_source(*args, **kwargs):
            # Filter files by owner value
            if self.owner_value in source_file.owners:
                yield source_file

    @property
    def name(self) -> str:
        return self.owner_value

    def __iter__(self) -> Iterator[TFile]:
        return self.files_generator()

    def __repr__(self) -> str:
        return f"CodeOwner(owner_type={self.owner_type}, owner_value={self.owner_value})"
