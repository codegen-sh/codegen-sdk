from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from codegen.sdk.enums import ProgrammingLanguage

if TYPE_CHECKING:
    from codegen.sdk.codebase.codebase_graph import CodebaseGraph


class ConfigParser(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def parse_configs(self, codebase_graph: "CodebaseGraph"): ...


def get_config_parser_for_language(language: ProgrammingLanguage, codebase_graph: "CodebaseGraph") -> ConfigParser | None:
    from codegen.sdk.typescript.config_parser import TSConfigParser

    if language == ProgrammingLanguage.TYPESCRIPT:
        return TSConfigParser(codebase_graph)

    return None
