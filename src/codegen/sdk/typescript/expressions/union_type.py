from typing import Generic, TypeVar

from codegen.sdk.core.expressions.union_type import UnionType
from codegen.shared.decorators.docs import ts_apidoc

Parent = TypeVar("Parent")


@ts_apidoc
class TSUnionType(UnionType["TSType", Parent], Generic[Parent]):
    """Union type

    Examples:
        string | number
    """

    pass
