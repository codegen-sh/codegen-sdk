from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from codegen_sdk.core.statements.block_statement import BlockStatement
from codegen_sdk.typescript.detached_symbols.code_block import TSCodeBlock
from codegen_sdk.typescript.interfaces.has_block import TSHasBlock
from codegen_sdk.writer_decorators import apidoc

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent", bound="TSCodeBlock")


@apidoc
class TSBlockStatement(BlockStatement[Parent], TSHasBlock, Generic[Parent]):
    """Statement which contains a block."""
