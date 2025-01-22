from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.enums import ProgrammingLanguage

if TYPE_CHECKING:
    from graph_sitter.core.codebase import Codebase


class Plugin(ABC):
    language: ProgrammingLanguage

    @abstractmethod
    def execute(self, codebase: "Codebase"): ...
    def register_api(self, method: str, label: str, node: Editable):
        pass
