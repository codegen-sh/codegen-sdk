from typing import Generic, TypeVar, override

from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Expression
from graph_sitter.core.expressions.builtin import Builtin
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import apidoc, noapidoc

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
