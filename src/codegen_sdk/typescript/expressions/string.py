from typing import TYPE_CHECKING, Generic, TypeVar

from graph_sitter.core.expressions import Expression, String
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.writer_decorators import ts_apidoc
from tree_sitter import Node as TSNode

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


Parent = TypeVar("Parent", bound="Expression")


@ts_apidoc
class TSString(String, Generic[Parent]):
    """A TypeScript string node representing both literal strings and template strings.

    This class handles both regular string literals and template strings in TypeScript,
    providing functionality to parse and manage template string expressions. It extends
    the base String class with TypeScript-specific capabilities.

    Attributes:
        expressions (list): A list of parsed expressions from template string substitutions.
            Empty for regular string literals.
    """

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent=parent)
        if ts_node.type == "template_string":
            substitutions = [x for x in ts_node.named_children if x.type == "template_substitution"]
            self.expressions = [self._parse_expression(x.named_children[0]) for x in substitutions]
        else:
            self.expressions = []
