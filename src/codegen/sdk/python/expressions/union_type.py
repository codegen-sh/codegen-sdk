from typing import TYPE_CHECKING, Generic, TypeVar

from codegen.sdk.core.expressions.union_type import UnionType
from codegen.utils.decorators.docs import py_apidoc

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent")


@py_apidoc
class PyUnionType(UnionType["PyType", Parent], Generic[Parent]):
    """Union type

    Examples:
        str | int
    """

    pass
