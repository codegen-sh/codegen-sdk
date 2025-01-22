import itertools
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from typing_extensions import deprecated

from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions.expression import Expression
from codegen_sdk.core.interfaces.chainable import Chainable
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.extensions.autocommit import reader
from codegen_sdk.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    from codegen_sdk.core.interfaces.importable import Importable
    from codegen_sdk.core.symbol import Symbol


Parent = TypeVar("Parent", bound="Editable")


@apidoc
class Type(Expression[Parent], Chainable, ABC, Generic[Parent]):
    """Abstract representation of a type
    Used to store the types of variables, parameters, or return values in functions, classes, etc.
    """

    @noapidoc
    @abstractmethod
    def _compute_dependencies(self, usage_type: UsageKind, dest: "Importable"): ...

    @property
    @deprecated("Use resolved_types instead for internal uses")
    @noapidoc
    @reader
    def resolved_symbol(self) -> "Symbol | str | None":
        from codegen_sdk.core.symbol import Symbol

        for resolved in self.resolved_types:
            if isinstance(resolved, Symbol):
                return resolved
        return None

    @property
    @noapidoc
    def descendant_symbols(self) -> list["Importable"]:
        """Returns the nested symbols of the importable object, including itself."""
        return list(itertools.chain.from_iterable(child.descendant_symbols for child in self.children))
