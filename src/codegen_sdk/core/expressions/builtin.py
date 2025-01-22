from collections.abc import Generator
from typing import TYPE_CHECKING, Self, override

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.interfaces.chainable import Chainable
from graph_sitter.core.interfaces.has_attribute import HasAttribute
from graph_sitter.extensions.autocommit import reader
from graph_sitter.writer_decorators import noapidoc

if TYPE_CHECKING:
    from graph_sitter.core.external_module import ExternalModule


@noapidoc
class Builtin(Chainable, HasAttribute):
    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        # TODO: resolve builtin type
        yield ResolutionStack(self)

    @noapidoc
    @override
    def resolve_attribute(self, name: str) -> "ExternalModule | None":
        # HACK/TODO
        return None
        # return ExternalModule(self.ts_node, self.file_node_id, self.G, name)
