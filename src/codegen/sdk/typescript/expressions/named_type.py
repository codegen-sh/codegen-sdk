from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from codegen.sdk.core.expressions.named_type import NamedType
from codegen.shared.decorators.docs import ts_apidoc

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

Parent = TypeVar("Parent")


@ts_apidoc
class TSNamedType(NamedType[Parent]):
    """Named type
    Examples:
        string.
    """

    def _get_name_node(self) -> TSNode | None:
        return self.ts_node
