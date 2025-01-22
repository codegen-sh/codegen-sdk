from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Self, TypeVar

from graph_sitter.codebase.codebase_graph import CodebaseGraph
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.statements.statement import Statement
from graph_sitter.core.symbol_groups.collection import Collection
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import apidoc, noapidoc
from tree_sitter import Node as TSNode

if TYPE_CHECKING:
    from graph_sitter.core.detached_symbols.code_block import CodeBlock
    from graph_sitter.core.file import SourceFile
    from graph_sitter.core.import_resolution import Import


TSourceFile = TypeVar("TSourceFile", bound="SourceFile")
TImport = TypeVar("TImport", bound="Import")
TCodeBlock = TypeVar("TCodeBlock", bound="CodeBlock")


@apidoc
class ImportStatement(Statement[TCodeBlock], Generic[TSourceFile, TImport, TCodeBlock]):
    """Abstract representation of a single import statement that appears in a file. One import
    statement can import multiple symbols from a single source.

    Attributes:
        imports: A collection of the individual imports this statement represents
    """

    imports: Collection[TImport, Self]

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: TCodeBlock, pos: int) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind = UsageKind.BODY, dest: HasName | None = None) -> None:
        # Skip computing dependencies for import statements, since it is done during import resolution step
        pass

    def _smart_remove(self, child, *args, **kwargs) -> bool:
        if self.imports.uncommitted_len == 1 and child.ts_node.is_named:
            self.remove()
            return True
        return super()._smart_remove(child, *args, **kwargs)
