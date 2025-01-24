"""Dataclasses used by the sandboxes server APIs"""

from pydantic import BaseModel

from codegen.runner.enums.warmup_state import WarmupState
from codegen.runner.models.codemod import BranchConfig, Codemod, CodemodRunResult, CreatedBranch, GroupingConfig

SANDBOX_SERVER_PORT = 4000
EPHEMERAL_SANDBOX_SERVER_PORT = 4001

# APIs
SIGNAL_SHUTDOWN_ENDPOINT = "/signal_shutdown"
DIFF_ENDPOINT = "/diff"
BRANCH_ENDPOINT = "/branch"

# Ephemeral sandbox apis
RUN_ON_STRING_ENDPOINT = "/run_on_string"


class ServerInfo(BaseModel):
    repo_id: int = 0
    container_id: str = ""
    is_running_codemod: bool = False
    is_shutting_down: bool = False
    warmup_state: WarmupState = WarmupState.PENDING
    label: str | None = ""


class UtilizationMetrics(BaseModel):
    container_id: str
    timestamp: str
    memory_rss_gb: float
    memory_vms_gb: float
    cpu_percent: float
    threads_count: int
    open_files_count: int


class SignalShutdownResponse(BaseModel):
    is_ready_to_shutdown: bool


class GetDiffRequest(BaseModel):
    codemod: Codemod
    max_transactions: int | None = None
    max_seconds: int | None = None


class GetDiffResponse(BaseModel):
    result: CodemodRunResult


class CreateBranchRequest(BaseModel):
    codemod: Codemod
    grouping_config: GroupingConfig
    branch_config: BranchConfig


class CreateBranchResponse(BaseModel):
    results: list[CodemodRunResult] | None = None
    branches: list[CreatedBranch] | None = None
    num_flags: int | None = None
    group_segments: list[str] | None = None


class GetRunOnStringRequest(BaseModel):
    codemod_source: str
    language: str
    files: dict[str, str]


class GetRunOnStringResult(BaseModel):
    result: CodemodRunResult
