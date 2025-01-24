from abc import abstractmethod
from typing import TYPE_CHECKING

from codegen.sdk.core.external.external_process import ExternalProcess
from codegen.sdk.enums import ProgrammingLanguage

if TYPE_CHECKING:
    from codegen.sdk.codebase.codebase_graph import CodebaseGraph


class DependencyManager(ExternalProcess):
    """Manages dependencies for the given repository.

    Handles reading, installing, and managing any dependency-based operations.
    """

    @abstractmethod
    def parse_dependencies(self):
        pass

    @abstractmethod
    def install_dependencies(self):
        pass

    @abstractmethod
    def remove_dependencies(self):
        pass


def get_dependency_manager(language: ProgrammingLanguage, codebase_graph: "CodebaseGraph", enabled: bool = False) -> DependencyManager | None:
    from codegen.sdk.typescript.external.dependency_manager import TypescriptDependencyManager

    ts_enabled = enabled or codebase_graph.config.feature_flags.ts_dependency_manager
    if language == ProgrammingLanguage.TYPESCRIPT:
        if ts_enabled:
            return TypescriptDependencyManager(repo_path=codebase_graph.repo_path, base_path=codebase_graph.projects[0].base_path)

    return None
