from typing import Generic, TypeVar, override

from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.expressions.builtin import Builtin
from codegen_sdk.core.interfaces.has_name import HasName
from codegen_sdk.extensions.autocommit import commiter
from codegen_sdk.writer_decorators import apidoc, noapidoc

Parent = TypeVar("Parent", bound="Expression")


@apidoc
class Number(Expression[Parent], Builtin, Generic[Parent]):
    """A number value.

    eg. 1, 2.0, 3.14
    """

    @noapidoc
    @commiter
    @override
    def _compute_dependencies(self, usage_type: UsageKind, dest: HasName | None = None) -> None:
        pass
