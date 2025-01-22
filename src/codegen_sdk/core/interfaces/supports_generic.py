from typing import TYPE_CHECKING, Generic, Self

from graph_sitter.core.expressions.named_type import NamedType
from graph_sitter.core.symbol import Symbol
from graph_sitter.core.symbol_groups.type_parameters import TypeParameters
from graph_sitter.extensions.utils import cached_property
from graph_sitter.writer_decorators import noapidoc
from typing_extensions import TypeVar

if TYPE_CHECKING:
    from graph_sitter.core.expressions import Type

TType = TypeVar("TType", bound="Type")


class SupportsGenerics(Symbol, Generic[TType]):
    type_parameters: TypeParameters[TType, Self] | None = None

    @cached_property
    @noapidoc
    def generics(self) -> dict[str, TType]:
        if self.type_parameters:
            return {param.name: param for param in self.type_parameters if isinstance(param, NamedType)}
        return {}
