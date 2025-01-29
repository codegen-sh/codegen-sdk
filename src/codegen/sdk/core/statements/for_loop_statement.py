from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Generic, Self, TypeVar

from codegen.sdk.core.autocommit import reader
from codegen.sdk.core.interfaces.chainable import Chainable
from codegen.sdk.core.interfaces.has_block import HasBlock
from codegen.sdk.core.statements.block_statement import BlockStatement
from codegen.sdk.core.statements.statement import StatementType
from codegen.sdk.core.symbol_groups.collection import Collection
from codegen.shared.decorators.docs import apidoc, noapidoc

if TYPE_CHECKING:
    from codegen.sdk.core.detached_symbols.code_block import CodeBlock
    from codegen.sdk.core.expressions import Expression
    from codegen.sdk.core.import_resolution import Import, WildcardImport
    from codegen.sdk.core.symbol import Symbol


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

    @noapidoc
    @reader
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
