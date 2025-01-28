from __future__ import annotations

from typing import TYPE_CHECKING

from codegen.sdk.core.assignment import Assignment
from codegen.sdk.core.expressions.multi_expression import MultiExpression
from codegen.sdk.extensions.autocommit import reader
from codegen.sdk.python.symbol import PySymbol
from codegen.sdk.python.symbol_groups.comment_group import PyCommentGroup
from codegen.shared.decorators.docs import noapidoc, py_apidoc

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

    from codegen.sdk.codebase.codebase_graph import CodebaseGraph
    from codegen.sdk.core.node_id_factory import NodeId
    from codegen.sdk.python.statements.assignment_statement import PyAssignmentStatement


@py_apidoc
class PyAssignment(Assignment["PyAssignmentStatement"], PySymbol):
    """An abstract representation of a assignment in python.

    This includes assignments of variables to functions, other variables, class instantiations, etc.
    """

    @noapidoc
    @classmethod
    def from_assignment(cls, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: PyAssignmentStatement) -> MultiExpression[PyAssignmentStatement, PyAssignment]:
        if ts_node.type not in ["assignment", "augmented_assignment"]:
            msg = f"Unknown assignment type: {ts_node.type}"
            raise ValueError(msg)

        left_node = ts_node.child_by_field_name("left")
        right_node = ts_node.child_by_field_name("right")
        assignments = cls._from_left_and_right_nodes(ts_node, file_node_id, G, parent, left_node, right_node)
        return MultiExpression(ts_node, file_node_id, G, parent, assignments)

    @classmethod
    def from_named_expression(cls, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: PyAssignmentStatement) -> MultiExpression[PyAssignmentStatement, PyAssignment]:
        """Creates a MultiExpression from a Python named expression.

        Creates assignments from a named expression node ('walrus operator' :=) by parsing its name and value fields.

        Args:
            ts_node (TSNode): The TreeSitter node representing the named expression.
            file_node_id (NodeId): The identifier of the file containing this node.
            G (CodebaseGraph): The codebase graph instance.
            parent (Parent): The parent node that contains this expression.

        Returns:
            MultiExpression[Parent, PyAssignment]: A MultiExpression containing the assignments created from the named expression.

        Raises:
            ValueError: If the provided ts_node is not of type 'named_expression'.
        """
        if ts_node.type != "named_expression":
            msg = f"Unknown assignment type: {ts_node.type}"
            raise ValueError(msg)

        left_node = ts_node.child_by_field_name("name")
        right_node = ts_node.child_by_field_name("value")
        assignments = cls._from_left_and_right_nodes(ts_node, file_node_id, G, parent, left_node, right_node)
        return MultiExpression(ts_node, file_node_id, G, parent, assignments)

    @property
    @reader
    def comment(self) -> PyCommentGroup | None:
        """Returns the comment group associated with the symbol.

        Retrieves and returns any comments associated with the symbol. These comments are typically
        located above or adjacent to the symbol in the source code.

        Args:
            self: The symbol instance to retrieve comments for.

        Returns:
            PyCommentGroup | None: A comment group object containing the symbol's comments if they exist,
            None otherwise.
        """
        # HACK: This is a temporary solution until comments are fixed
        return PyCommentGroup.from_symbol_comments(self)

    @property
    @reader
    def inline_comment(self) -> PyCommentGroup | None:
        """A property that retrieves the inline comment group associated with a symbol.

        Retrieves any inline comments that are associated with this symbol. Inline comments are comments that appear on the same line as the code.

        Args:
            None

        Returns:
            PyCommentGroup | None: The inline comment group associated with the symbol, if one exists. Returns None if there are no inline comments.
        """
        # HACK: This is a temporary solution until comments are fixed
        return PyCommentGroup.from_symbol_inline_comments(self, self.ts_node.parent)
