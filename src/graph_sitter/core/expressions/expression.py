from __future__ import annotations

from typing import Generic, TypeVar

from graph_sitter.core.interfaces.chainable import Chainable
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.enums import NodeType
from graph_sitter.extensions.autocommit import reader
from graph_sitter.writer_decorators import apidoc

Parent = TypeVar("Parent", bound="Editable")


@apidoc
class Expression(Editable[Parent], Generic[Parent]):
    """Represents an arbitrary Expression, such as List, Dict, Binary Expression, String."""

    node_type: NodeType = NodeType.EXPRESSION

    @property
    @reader
    def resolved_value(self) -> Expression | list[Expression]:
        """Returns the resolved type of an Expression.

        Returns the inferred type of the expression. For example, a function call's resolved value will be its definition.

        Returns:
            Expression | list[Expression]: The resolved expression type(s). Returns a single Expression if there is only one resolved type,
            or a list of Expressions if there are multiple resolved types. Returns self if the expression is not resolvable or has no resolved types.
        """
        if isinstance(self, Chainable) and (resolved_types := self.resolved_types):
            if len(resolved_types) == 1:
                return resolved_types[0]
            return resolved_types
        return self
