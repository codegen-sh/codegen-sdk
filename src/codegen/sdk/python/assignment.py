from __future__ import annotations

from typing import TYPE_CHECKING

from codegen.sdk._proxy import proxy_property
from codegen.sdk.core.assignment import Assignment
from codegen.sdk.core.dataclasses.usage import Usage, UsageKind, UsageType
from codegen.sdk.core.expressions.multi_expression import MultiExpression
from codegen.sdk.enums import EdgeType
from codegen.sdk.extensions.autocommit import commiter, reader
from codegen.sdk.python.symbol import PySymbol
from codegen.sdk.python.symbol_groups.comment_group import PyCommentGroup
from codegen.shared.decorators.docs import noapidoc, py_apidoc

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

    from codegen.sdk.codebase.codebase_graph import CodebaseGraph
    from codegen.sdk.core.interfaces.has_name import HasName
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

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind | None = None, dest: HasName | None = None) -> None:
        super()._compute_dependencies(usage_type, dest)
        if len(self.parent.assignments)>=2:
            for assigment_sibling in self.parent.assignments:
                if assigment_sibling.name!=self.name:
                    self.G.add_edge(self.node_id,assigment_sibling.node_id,EdgeType.SYMBOL_USAGE,usage=Usage(match=self.get_name(),kind=UsageKind.ASSIGNMENT_SIBLING,usage_type=UsageType.DIRECT,usage_symbol=self,imported_by=None))

    @proxy_property
    @reader(cache=False)
    def usages(self, usage_types: UsageType | None = None) -> list[Usage]:
        """Returns a list of usages of the PyAssignment object.

        Retrieves all locations where the exportable object is used in the codebase. By default, returns all usages, such as imports or references within the same file.

        Args:
            usage_types (UsageType | None): Specifies which types of usages to include in the results. Default is any usages.

        Returns:
            list[Usage]: A sorted list of Usage objects representing where this exportable is used, ordered by source location in reverse.

        Raises:
            ValueError: If no usage types are specified or if only ALIASED and DIRECT types are specified together.

        Note:
            This method can be called as both a property or a method. If used as a property, it is equivalent to invoking it without arguments.
        """
        if usage_types == UsageType.DIRECT | UsageType.ALIASED:
            msg = "Combination of only Aliased and Direct usages makes no sense"
            raise ValueError(msg)

        assert self.node_id is not None
        usages_to_return = []
        in_edges = self.G.in_edges(self.node_id)
        for edge in in_edges:
            meta_data = edge[2]
            if meta_data.type == EdgeType.SYMBOL_USAGE:
                usage = meta_data.usage
                if usage.kind==UsageKind.ASSIGNMENT_SIBLING:
                    sibling = self.G.get_node(edge[0])
                    for s_edge in self.G.in_edges(sibling.node_id):
                        if s_edge[2].usage.kind!=UsageKind.ASSIGNMENT_SIBLING:
                            usages_to_return.append(usage)
                            break
                elif usage_types is None or usage.usage_type in usage_types:
                    usages_to_return.append(usage)
        return sorted(dict.fromkeys(usages_to_return), key=lambda x: x.match.ts_node.start_byte if x.match else x.usage_symbol.ts_node.start_byte, reverse=True)
