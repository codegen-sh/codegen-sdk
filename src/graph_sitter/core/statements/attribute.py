from __future__ import annotations

import itertools
from abc import abstractmethod
from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from tree_sitter import Node as TSNode

from graph_sitter.codebase.codebase_graph import CodebaseGraph
from graph_sitter.core.assignment import Assignment
from graph_sitter.core.autocommit import writer
from graph_sitter.core.interfaces.chainable import Chainable
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.core.interfaces.usable import Usable
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.statements.assignment_statement import AssignmentStatement
from graph_sitter.core.statements.statement import StatementType
from graph_sitter.extensions.autocommit import reader
from graph_sitter.extensions.resolution import ResolutionStack
from graph_sitter.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    from graph_sitter.core.detached_symbols.code_block import CodeBlock

TCodeBlock = TypeVar("TCodeBlock", bound="CodeBlock | None")
TAssignment = TypeVar("TAssignment", bound="Assignment")


@apidoc
class Attribute(AssignmentStatement[TCodeBlock, TAssignment], Usable, Chainable, Generic[TCodeBlock, TAssignment]):
    """Abstract representation of an attribute on a class definition."""

    statement_type = StatementType.CLASS_ATTRIBUTE
    assignment: TAssignment

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: TCodeBlock, pos: int, assignment_node: TSNode) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos=pos, assignment_node=assignment_node)
        self.assignment = self.assignments[0]
        self._name_node = self.assignment.get_name()

    @abstractmethod
    def _get_name_node(self) -> TSNode:
        """Returns the ID node from the root node of the symbol."""

    @property
    @abstractmethod
    def is_private(self) -> bool:
        """Indicates whether the attribute is private.

        Determines if the attribute is a private class attribute by checking if it follows Python's private naming convention (i.e., starts with an underscore).

        Returns:
            bool: True if the attribute is private (starts with underscore), False otherwise.
        """
        ...

    @property
    @abstractmethod
    def is_optional(self) -> bool:
        """Returns whether the attribute is optional.

        Determines if an attribute's type annotation indicates it is optional/nullable. For example,
        if the attribute's type is `Optional[str]` or `str | None`, this will return True.

        Returns:
            bool: True if the attribute is marked as optional/nullable, False otherwise.
        """

    @writer
    def set_value(self, value: str) -> None:
        """Sets the value of a node's assignment.

        Updates the value of a node's assignment to the specified string value.

        Args:
            value (str): The new value to set for the assignment.

        Returns:
            None
        """
        self.assignment.set_value(value)

    @property
    @noapidoc
    def descendant_symbols(self) -> list[Importable]:
        return list(itertools.chain.from_iterable(assignment.descendant_symbols for assignment in self.assignments))

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        yield from self.with_resolution_frame(self.assignments[0])
