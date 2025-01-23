from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codegen.sdk.codebase.codebase_graph import CodebaseGraph


class Parseable(ABC):
    @abstractmethod
    def parse(self, G: "CodebaseGraph") -> None:
        """Adds itself and its children to the codebase graph."""
