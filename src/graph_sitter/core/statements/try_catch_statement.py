from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Generic, TypeVar

from graph_sitter.core.interfaces.has_block import HasBlock
from graph_sitter.core.statements.block_statement import BlockStatement
from graph_sitter.core.statements.statement import StatementType
from graph_sitter.writer_decorators import apidoc

if TYPE_CHECKING:
    from graph_sitter.core.detached_symbols.code_block import CodeBlock


Parent = TypeVar("Parent", bound="CodeBlock")


@apidoc
class TryCatchStatement(BlockStatement[Parent], HasBlock, ABC, Generic[Parent]):
    """Abstract representation of the try catch statement block.

    Attributes:
        code_block: The code block that may trigger an exception
        finalizer: The code block executed regardless of if an exception is thrown or not
    """

    statement_type = StatementType.TRY_CATCH_STATEMENT
    finalizer: BlockStatement | None = None
