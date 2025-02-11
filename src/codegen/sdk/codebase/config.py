import os
from typing import Self

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field

from codegen.git.repo_operator.local_repo_operator import LocalRepoOperator
from codegen.git.repo_operator.repo_operator import RepoOperator
from codegen.git.schemas.repo_config import RepoConfig
from codegen.git.utils.file_utils import split_git_path
from codegen.git.utils.language import determine_project_language
from codegen.sdk.secrets import Secrets
from codegen.shared.enums.programming_language import ProgrammingLanguage

HARD_MAX_AI_LIMIT = 500  # Global limit for AI requests


class SessionOptions(BaseModel):
    """Options for a session. A session is a single codemod run."""

    model_config = ConfigDict(frozen=True)
    max_seconds: int | None = None
    max_transactions: int | None = None
    max_ai_requests: int = Field(default=150, le=HARD_MAX_AI_LIMIT)


class GSFeatureFlags(BaseModel):
    """Config for building the graph sitter graph. These are non-repo specific options that are set per-usecase.

    Attributes:
        debug: Warning if there are errors during parsing (such as unimplemented nodes)
        verify_graph: Verify the accuracy of the graph between resets. Will result in lag
        method_usages: Resolve . usages
    """

    model_config = ConfigDict(frozen=True)
    debug: bool = False
    verify_graph: bool = False
    track_graph: bool = False  # Track the initial graph state
    method_usages: bool = True
    sync_enabled: bool = True
    ts_dependency_manager: bool = False  # Enable Typescript Dependency Manager
    ts_language_engine: bool = False  # Enable Typescript Language Engine
    v8_ts_engine: bool = False  # Enable V8 Based Typescript Language Engine Instead of NodeJS
    full_range_index: bool = False
    ignore_process_errors: bool = True  # Ignore errors from dependency manager and language engine
    import_resolution_overrides: dict[str, str] = {}  # Override import resolution for specific modules
    disable_graph: bool = False  # Turn of graph generation entirely. Speeds up parsing but disables usages and dependencies
    generics: bool = True  # Enable parsing of generic types


DefaultFlags = GSFeatureFlags(sync_enabled=False)

TestFlags = GSFeatureFlags(debug=True, track_graph=True, verify_graph=True, full_range_index=True)
LintFlags = GSFeatureFlags(method_usages=False)
ParseTestFlags = GSFeatureFlags(debug=False, track_graph=False)


class ProjectConfig(BaseModel):
    """Context for a codebase. A codebase is a set of files in a directory."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    repo_operator: RepoOperator

    # TODO: clean up these fields. Duplicated across RepoConfig and CodebaseContext
    base_path: str | None = None
    subdirectories: list[str] | None = None
    programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON

    @classmethod
    def from_path(cls, path: str, programming_language: ProgrammingLanguage | None = None) -> Self:
        # Split repo_path into (git_root, base_path)
        repo_path = os.path.abspath(path)
        git_root, base_path = split_git_path(repo_path)
        subdirectories = [base_path] if base_path else None
        programming_language = programming_language or determine_project_language(repo_path)
        repo_config = RepoConfig.from_repo_path(repo_path=git_root, language=programming_language, subdirectories=subdirectories)
        # Create main project
        return cls(
            repo_operator=LocalRepoOperator(repo_config=repo_config),
            programming_language=programming_language,
            base_path=base_path,
            subdirectories=subdirectories,
        )

    @classmethod
    def from_repo_operator(cls, repo_operator: RepoOperator, programming_language: ProgrammingLanguage | None = None, base_path: str | None = None) -> Self:
        return cls(
            repo_operator=repo_operator,
            programming_language=programming_language or determine_project_language(repo_operator.repo_path),
            base_path=base_path,
            subdirectories=[base_path] if base_path else None,
        )


class CodebaseConfig(BaseModel):
    """Configuration for a Codebase. There can be 1 -> many codebases in a single repo
    TODO: replace with a DB model (move codebase columns off of RepoModel)
    """

    model_config = ConfigDict(frozen=True)
    secrets: Secrets = Secrets()
    feature_flags: GSFeatureFlags = DefaultFlags


DefaultConfig = CodebaseConfig()
