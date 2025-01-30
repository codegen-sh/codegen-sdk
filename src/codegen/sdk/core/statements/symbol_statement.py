from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from codegen.sdk.core.statements.statement import Statement, StatementType
from codegen.sdk.extensions.autocommit import reader
from codegen.shared.decorators.docs import apidoc, noapidoc

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

    from codegen.sdk.codebase.codebase_graph import CodebaseGraph
    from codegen.sdk.core.dataclasses.usage import UsageKind
    from codegen.sdk.core.detached_symbols.code_block import CodeBlock
    from codegen.sdk.core.detached_symbols.function_call import FunctionCall
    from codegen.sdk.core.interfaces.has_name import HasName
    from codegen.sdk.core.interfaces.importable import Importable
    from codegen.sdk.core.node_id_factory import NodeId
    from codegen.sdk.core.symbol import Symbol


Parent = TypeVar("Parent", bound="CodeBlock")
Child = TypeVar("Child", bound="Symbol")


@apidoc
class SymbolStatement(Statement[Parent], Generic[Parent, Child]):
    """A statement that represents a symbol definition in a codeblock.

    Examples include:
    - a function definition, class definition, global variable assignment
    """

    statement_type = StatementType.SYMBOL_STATEMENT
    symbol: Child

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: Parent, pos: int, symbol_node: TSNode | None = None) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        self.symbol = self.G.parser.parse_expression(symbol_node or ts_node, file_node_id, G, parent=self)

    def _compute_dependencies(self, usage_type: UsageKind, dest: HasName | None = None) -> None:
        pass

    @property
    @reader
    def function_calls(self) -> list[FunctionCall]:
        """Returns all function calls contained within the symbol associated with this statement.

        This property retrieves all function call nodes from the statement's underlying symbol. This is useful for tasks
        like renaming function invocations or analyzing call patterns. Note that this operation may trigger a reparse of
        the file and could be slow.

        Returns:
            list[FunctionCall]: A list of FunctionCall objects representing all function calls within the symbol.

        Note:
            Consider using function.call_sites instead if you already know which specific function you're looking for,
            as it will be more performant.
        """
        return self.symbol.function_calls

    @property
    @noapidoc
    def descendant_symbols(self) -> list[Importable]:
        """Returns the nested symbols of the importable object."""
        return self.symbol.descendant_symbols
