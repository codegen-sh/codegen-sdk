from typing import Generic, TypeVar

from codegen_sdk.core.detached_symbols.function_call import FunctionCall
from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.core.interfaces.has_value import HasValue
from codegen_sdk.core.interfaces.wrapper_expression import IWrapper
from codegen_sdk.extensions.autocommit import reader
from codegen_sdk.writer_decorators import apidoc

Parent = TypeVar("Parent", bound="Editable")


@apidoc
class AwaitExpression(Expression[Parent], HasValue, IWrapper, Generic[Parent]):
    """An awaited expression, only found in asynchronous contexts, e.g. await(foo(bar))"""

    def __init__(self, ts_node, file_node_id, G, parent: Parent):
        super().__init__(ts_node, file_node_id, G, parent=parent)
        value_node = self.ts_node.named_children[0]
        self._value_node = self.G.parser.parse_expression(value_node, self.file_node_id, self.G, parent) if value_node else None

    @property
    @reader
    def function_calls(self) -> list[FunctionCall]:
        """Gets all function calls within the await expression.

        Returns:
            list[FunctionCall]: A list of function call nodes contained within the await expression's value.
        """
        return self.resolve().function_calls
