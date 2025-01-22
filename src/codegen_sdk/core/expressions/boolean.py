from typing import Generic, TypeVar, override

from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Expression
from graph_sitter.core.expressions.builtin import Builtin
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import apidoc, noapidoc

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
