from typing import TypeVar

from codegen_sdk.core.expressions.ternary_expression import TernaryExpression
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.writer_decorators import ts_apidoc

Parent = TypeVar("Parent", bound="Editable")


@ts_apidoc
class TSTernaryExpression(TernaryExpression[Parent]):
    """Any ternary expression in the code where a condition will determine branched execution"""

    def __init__(self, ts_node, file_node_id, G, parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent=parent)
        self.condition = self.child_by_field_name("condition")
        self.consequence = self.child_by_field_name("consequence")
        self.alternative = self.child_by_field_name("alternative")
