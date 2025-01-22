from typing import TYPE_CHECKING, Generic, Self, TypeVar

from graph_sitter.core.autocommit import reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.builtin import Builtin
from graph_sitter.core.expressions.expression import Expression
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.symbol_groups.collection import Collection
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import apidoc, noapidoc
from tree_sitter import Node as TSNode

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


Parent = TypeVar("Parent", bound="Expression")


@apidoc
class String(Expression[Parent], Builtin, Generic[Parent]):
    """GraphSitter representation of String.

    Attributes:
        content: The content of the string
        expressions: embedded expressions in the string, only applicable for templated or formatted strings
    """

    content: str
    content_nodes: Collection[Expression[Editable], Self]  # string content is a collection of string_fragments and escape_sequences in TS and a single string_content in Python
    expressions: list[Expression[Editable]]  # expressions in the string, only applicable for template strings

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent=parent)
        content_children = list(self.children_by_field_types({"string_content", "string_fragment", "escape_sequence"}))
        self.content_nodes = Collection(ts_node, self.file_node_id, self.G, self, delimiter="", children=content_children)
        self.content = "".join(x.ts_node.text.decode("utf-8") for x in content_children)

    @reader
    def __eq__(self, other: object) -> bool:
        if isinstance(other, str) and other == self.content:
            return True
        return super().__eq__(other)

    def __str__(self):
        return self.content

    def __hash__(self):
        return super().__hash__()

    @property
    @reader
    def with_quotes(self) -> str:
        """Retrieves the string representation with quotation marks.

        Returns:
            str: The string value with its surrounding quotation marks.
        """
        return self.source

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind | None = None, dest: HasName | None = None) -> None:
        # If the string is a template string, we need to compute the dependencies of the string content
        for expression in self.expressions:
            expression._compute_dependencies(usage_type, dest)
