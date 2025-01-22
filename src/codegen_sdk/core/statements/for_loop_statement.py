from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Generic, Self, TypeVar

from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.import_resolution import Import, WildcardImport
from codegen_sdk.core.interfaces.chainable import Chainable
from codegen_sdk.core.interfaces.has_block import HasBlock
from codegen_sdk.core.statements.block_statement import BlockStatement
from codegen_sdk.core.statements.statement import StatementType
from codegen_sdk.core.symbol import Symbol
from codegen_sdk.core.symbol_groups.collection import Collection
from codegen_sdk.writer_decorators import apidoc

if TYPE_CHECKING:
    from codegen_sdk.core.detached_symbols.code_block import CodeBlock


Parent = TypeVar("Parent", bound="CodeBlock")


@apidoc
class ForLoopStatement(BlockStatement[Parent], HasBlock, ABC, Generic[Parent]):
    """Abstract representation of the for loop.

    Attributes:
        code_block: The code block that is executed in each iteration of the loop
    """

    statement_type = StatementType.FOR_LOOP_STATEMENT
    item: Expression[Self] | None = None
    iterable: Expression[Self]

    def resolve_name(self, name: str, start_byte: int | None = None) -> Symbol | Import | WildcardImport | None:
        if self.item and isinstance(self.iterable, Chainable):
            if start_byte is None or start_byte > self.iterable.end_byte:
                if name == self.item:
                    for frame in self.iterable.resolved_type_frames:
                        if frame.generics:
                            return next(iter(frame.generics.values()))
                        return frame.top.node
                elif isinstance(self.item, Collection):
                    for idx, item in enumerate(self.item):
                        if item == name:
                            for frame in self.iterable.resolved_type_frames:
                                if frame.generics and len(frame.generics) > idx:
                                    return list(frame.generics.values())[idx]
                                return frame.top.node
        return super().resolve_name(name, start_byte)
