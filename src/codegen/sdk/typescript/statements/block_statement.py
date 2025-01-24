from __future__ import annotations

from typing import Generic, TypeVar

from codegen.sdk.core.statements.block_statement import BlockStatement
from codegen.sdk.typescript.detached_symbols.code_block import TSCodeBlock
from codegen.sdk.typescript.interfaces.has_block import TSHasBlock
from codegen.shared.decorators.docs import apidoc

Parent = TypeVar("Parent", bound="TSCodeBlock")


@apidoc
class TSBlockStatement(BlockStatement[Parent], TSHasBlock, Generic[Parent]):
    """Statement which contains a block."""
