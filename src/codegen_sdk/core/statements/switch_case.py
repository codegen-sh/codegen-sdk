from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Self, TypeVar

from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.interfaces.has_name import HasName
from codegen_sdk.core.statements.block_statement import BlockStatement
from codegen_sdk.extensions.autocommit import commiter
from codegen_sdk.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    from codegen_sdk.core.assignment import Assignment
    from codegen_sdk.core.detached_symbols.code_block import CodeBlock
    from codegen_sdk.core.statements.switch_statement import SwitchStatement

Parent = TypeVar("Parent", bound="CodeBlock[SwitchStatement, Assignment]")


@apidoc
class SwitchCase(BlockStatement[Parent], Generic[Parent]):
    """Abstract representation for a switch case.

    Attributes:
        code_block: The code block that is executed if the condition is met
        condition: The condition which triggers this case
    """

    condition: Expression[Self] | None = None

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind | None = None, dest: HasName | None = None) -> None:
        if self.condition:
            self.condition._compute_dependencies(usage_type, dest)
        super()._compute_dependencies(usage_type, dest)
