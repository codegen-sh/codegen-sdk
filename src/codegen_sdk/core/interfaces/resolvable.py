from abc import abstractmethod
from typing import TYPE_CHECKING, Generic

from typing_extensions import TypeVar

from codegen_sdk.core.autocommit import writer
from codegen_sdk.core.interfaces.chainable import Chainable
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.writer_decorators import noapidoc

if TYPE_CHECKING:
    pass
Parent = TypeVar("Parent", bound=Editable)


class Resolvable(Chainable[Parent], Generic[Parent]):
    """Represents a class resolved to another symbol during the compute dependencies step."""

    @abstractmethod
    @noapidoc
    @writer
    def rename_if_matching(self, old: str, new: str) -> None: ...
