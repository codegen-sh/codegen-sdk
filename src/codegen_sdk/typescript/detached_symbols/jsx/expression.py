from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from codegen_sdk.core.autocommit import reader, writer
from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.core.interfaces.has_name import HasName
from codegen_sdk.core.interfaces.unwrappable import Unwrappable
from codegen_sdk.extensions.autocommit import commiter
from codegen_sdk.writer_decorators import noapidoc, ts_apidoc

if TYPE_CHECKING:
    pass


@ts_apidoc
class JSXExpression(Unwrappable["Function | JSXElement | JSXProp"]):
    """Abstract representation of TSX/JSX expression"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statement

    @cached_property
    @reader
    def statement(self) -> Editable[Self] | None:
        """Returns the editable component of this JSX expression.

        Retrieves the editable contained within this JSX expression by accessing the second child node. Returns None if the JSX expression doesn't
        contain an editable object.

        Returns:
            Editable[Self]: A Editable object representing the statement of this JSX expression. None if the object doesn't have an Editable object.
        """
        return self._parse_expression(self.ts_node.named_children[0]) if len(self.ts_node.named_children) > 0 else None

    @commiter
    @noapidoc
    @override
    def _compute_dependencies(self, usage_type: UsageKind, dest: HasName | None = None) -> None:
        if self.statement:
            self.statement._compute_dependencies(usage_type, dest=dest)

    @writer
    def reduce_condition(self, bool_condition: bool, node: Editable) -> None:
        """Simplifies a JSX expression by reducing it based on a boolean condition.


        Args:
            bool_condition (bool): The boolean value to reduce the condition to.

        """
        if self.ts_node.parent.type == "jsx_attribute" and not bool_condition:
            node.edit(self.G.node_classes.bool_conversion[bool_condition])
        else:
            self.remove()

    @writer
    @override
    def unwrap(self, node: Expression | None = None):
        """Removes the brackets from a JSX expression.


        Returns:
            None
        """
        from codegen_sdk.typescript.detached_symbols.jsx.element import JSXElement
        from codegen_sdk.typescript.detached_symbols.jsx.prop import JSXProp

        if node is None:
            node = self
        if isinstance(node, JSXExpression | JSXElement | JSXProp):
            for child in self._anonymous_children:
                child.remove()
