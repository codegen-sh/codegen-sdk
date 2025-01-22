from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.enums import ProgrammingLanguage

if TYPE_CHECKING:
    from codegen_sdk.core.codebase import Codebase


class Plugin(ABC):
    language: ProgrammingLanguage

    @abstractmethod
    def execute(self, codebase: "Codebase"): ...
    def register_api(self, method: str, label: str, node: Editable):
        pass
