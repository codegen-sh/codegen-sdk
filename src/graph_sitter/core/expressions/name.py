from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Optional, Self, TypeVar, override

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.autocommit import reader, writer
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.expression import Expression
from graph_sitter.core.interfaces.resolvable import Resolvable
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    from graph_sitter.core.interfaces.has_name import HasName


Parent = TypeVar("Parent", bound="Expression")


@apidoc
class Name(Expression[Parent], Resolvable, Generic[Parent]):
    """Editable attribute on any given code objects that has a name.

    For example, function, classes, global variable, interfaces, attributes, parameters are all
    composed of a name.
    """

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        """Resolve the types used by this symbol."""
        if used := self.resolve_name(self.source, self.start_byte):
            yield from self.with_resolution_frame(used)

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind, dest: Optional["HasName | None "] = None) -> None:
        """Compute the dependencies of the export object."""
        edges = []
        for used_frame in self.resolved_type_frames:
            edges.extend(used_frame.get_edges(self, usage_type, dest, self.G))
        if self.G.config.feature_flags.debug:
            edges = list(dict.fromkeys(edges))
        self.G.add_edges(edges)

    @noapidoc
    @writer
    def rename_if_matching(self, old: str, new: str):
        if self.source == old:
            self.edit(new)
