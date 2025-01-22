from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Self, TypeVar

from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Expression
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.core.statements.block_statement import BlockStatement
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    from graph_sitter.core.assignment import Assignment
    from graph_sitter.core.detached_symbols.code_block import CodeBlock
    from graph_sitter.core.statements.switch_statement import SwitchStatement

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
