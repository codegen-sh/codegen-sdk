from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from codegen.sdk.core.expressions.named_type import NamedType
from codegen.shared.decorators.docs import py_apidoc

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

Parent = TypeVar("Parent")


@py_apidoc
class PyNamedType(NamedType[Parent], Generic[Parent]):
    """Named python type.

    Examples:
        int,str (builtin types)
        Path (classes)
    """

    def _get_name_node(self) -> TSNode | None:
        return self.ts_node
