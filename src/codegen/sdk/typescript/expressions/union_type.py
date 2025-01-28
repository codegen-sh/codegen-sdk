from typing import TYPE_CHECKING, Generic, TypeVar

from codegen.sdk.core.expressions.union_type import UnionType
from codegen.shared.decorators.docs import ts_apidoc

if TYPE_CHECKING:
    from codegen.sdk.typescript.expressions.type import TSType

Parent = TypeVar("Parent")


@ts_apidoc
class TSUnionType(UnionType["TSType", Parent], Generic[Parent]):
    """Union type

    Examples:
        string | number
    """

    pass
