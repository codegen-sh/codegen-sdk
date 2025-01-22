from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions.expression import Expression
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.core.interfaces.has_name import HasName
from codegen_sdk.extensions.autocommit import commiter
from codegen_sdk.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent", bound="Editable")


@apidoc
class Value(Expression[Parent], Generic[Parent]):
    """Editable attribute on code objects that has a value.

    For example, Functions, Classes, Assignments, Interfaces, Expressions, Arguments and Parameters all have values.

    See also HasValue.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.G.parser.log_unparsed(self.ts_node)

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind, dest: HasName | None = None):
        for node in self.children:
            node._compute_dependencies(usage_type, dest=dest)
