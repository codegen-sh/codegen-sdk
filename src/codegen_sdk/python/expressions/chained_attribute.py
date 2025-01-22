from typing import Generic, TypeVar

from codegen_sdk.core.expressions import Expression, Name
from codegen_sdk.core.expressions.chained_attribute import ChainedAttribute
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.writer_decorators import py_apidoc

Parent = TypeVar("Parent", bound="Editable")


@py_apidoc
class PyChainedAttribute(ChainedAttribute[Expression, Name, Parent], Generic[Parent]):
    """Abstract representation of a python chained attribute.
    This includes methods of python classes and module functions.
    """

    def __init__(self, ts_node, file_node_id, G, parent: Parent):
        super().__init__(ts_node, file_node_id, G, parent=parent, object=ts_node.child_by_field_name("object"), attribute=ts_node.child_by_field_name("attribute"))
