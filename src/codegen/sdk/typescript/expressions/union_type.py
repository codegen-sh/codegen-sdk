from typing import TYPE_CHECKING, Generic, TypeVar

from codegen.sdk.core.expressions.union_type import UnionType
from codegen.utils.decorators.docs import ts_apidoc

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent")


@ts_apidoc
class TSUnionType(UnionType["TSType", Parent], Generic[Parent]):
    """Union type

    Examples:
        string | number
    """

    pass
