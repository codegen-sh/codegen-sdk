from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from graph_sitter.codebase.codebase_graph import CodebaseGraph
from graph_sitter.core.autocommit import writer
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.expression import Expression
from graph_sitter.core.interfaces.chainable import Chainable
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.extensions.autocommit import commiter, reader
from graph_sitter.extensions.resolution import ResolutionStack
from graph_sitter.extensions.utils import TSNode
from graph_sitter.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent", bound="Expression")


@apidoc
class UnaryExpression(Expression[Parent], Chainable, Generic[Parent]):
    """Unary expression which is a single operation on a single operand. eg. -5, !true.

    Attributes:
        argument: The argument of the unary expression
    """

    argument: Expression[Self]

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent)
        self.argument = self._parse_expression(ts_node.child_by_field_name("argument"))

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        """Resolve the types used by this symbol."""
        yield from self.with_resolution_frame(self.argument)

    @commiter
    @noapidoc
    def _compute_dependencies(self, usage_type: UsageKind = UsageKind.BODY, dest: HasName | None = None) -> None:
        self.argument._compute_dependencies(usage_type, dest)

    @writer
    def reduce_condition(self, bool_condition: bool, node: Editable | None = None) -> None:
        """Simplifies a unary expression by reducing it based on a boolean condition.


        Args:
            bool_condition (bool): The boolean value to reduce the condition to.

        """
        if self.ts_node.type == "not_operator" or self.source.startswith("!"):
            self.parent.reduce_condition(not bool_condition, self)
        else:
            super().reduce_condition(bool_condition, node)
