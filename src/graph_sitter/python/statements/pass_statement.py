from __future__ import annotations

from typing import TYPE_CHECKING, override

from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.core.statements.statement import Statement, StatementType
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import noapidoc, py_apidoc

if TYPE_CHECKING:
    pass


@py_apidoc
class PyPassStatement(Statement["PyCodeBlock"]):
    """An abstract representation of a python pass statement."""

    statement_type = StatementType.PASS_STATEMENT

    @noapidoc
    @commiter
    @override
    def _compute_dependencies(self, usage_type: UsageKind, dest: HasName | None = None) -> None:
        pass
