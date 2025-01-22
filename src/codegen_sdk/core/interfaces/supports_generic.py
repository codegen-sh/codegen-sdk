from typing import TYPE_CHECKING, Generic, Self

from typing_extensions import TypeVar

from codegen_sdk.core.expressions.named_type import NamedType
from codegen_sdk.core.symbol import Symbol
from codegen_sdk.core.symbol_groups.type_parameters import TypeParameters
from codegen_sdk.extensions.utils import cached_property
from codegen_sdk.writer_decorators import noapidoc

if TYPE_CHECKING:
    from codegen_sdk.core.expressions import Type

TType = TypeVar("TType", bound="Type")


class SupportsGenerics(Symbol, Generic[TType]):
    type_parameters: TypeParameters[TType, Self] | None = None

    @cached_property
    @noapidoc
    def generics(self) -> dict[str, TType]:
        if self.type_parameters:
            return {param.name: param for param in self.type_parameters if isinstance(param, NamedType)}
        return {}
