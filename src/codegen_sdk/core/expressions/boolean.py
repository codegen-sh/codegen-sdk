from typing import Generic, TypeVar, override

from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.expressions.builtin import Builtin
from codegen_sdk.core.interfaces.has_name import HasName
from codegen_sdk.extensions.autocommit import commiter
from codegen_sdk.writer_decorators import apidoc, noapidoc

Parent = TypeVar("Parent", bound="Expression")


@apidoc
class Boolean(Expression[Parent], Builtin, Generic[Parent]):
    """A boolean value eg.

    True, False
    """

    def __bool__(self):
        return self.ts_node.type == "true"

    @noapidoc
    @commiter
    @override
    def _compute_dependencies(self, usage_type: UsageKind, dest: HasName | None = None) -> None:
        pass
