from pydantic import BaseModel, ConfigDict, Field

from codegen_git.repo_operator.repo_operator import RepoOperator
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.secrets import Secrets

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
    track_graph: bool = True  # Track the initial graph state
    method_usages: bool = True
    sync_enabled: bool = True
    ts_dependency_manager: bool = False  # Enable Typescript Dependency Manager
    ts_language_engine: bool = False  # Enable Typescript Language Engine
    v8_ts_engine: bool = False  # Enable V8 Based Typescript Language Engine Instead of NodeJS
    full_range_index: bool = False
    ignore_process_errors: bool = True  # Ignore errors from dependency manager and language engine
    import_resolution_overrides: dict[str, str] = {}  # Override import resolution for specific modules


DefaultFlags = GSFeatureFlags(sync_enabled=False)

TestFlags = GSFeatureFlags(debug=True, verify_graph=True, full_range_index=True)
LintFlags = GSFeatureFlags(method_usages=False)
ParseTestFlags = GSFeatureFlags(debug=False, track_graph=False)


class ProjectConfig(BaseModel):
    """Context for a codebase. A codebase is a set of files in a directory."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    repo_operator: RepoOperator
    base_path: str | None = None
    subdirectories: list[str] | None = None
    programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON


class CodebaseConfig(BaseModel):
    """Configuration for a Codebase. There can be 1 -> many codebases in a single repo
    TODO: replace with a DB model (move codebase columns off of RepoModel)
    """

    model_config = ConfigDict(frozen=True)
    secrets: Secrets = Secrets()
    feature_flags: GSFeatureFlags = DefaultFlags


DefaultConfig = CodebaseConfig()
