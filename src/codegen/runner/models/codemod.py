"""Dataclasses used by the sandbox runners"""

from datetime import datetime

from pydantic import BaseModel

from codegen.git.models.codemod_context import CodemodContext
from codegen.git.models.pr_options import PROptions
from codegen.sdk.codebase.flagging.groupers.enums import GroupBy


class Codemod(BaseModel):
    run_id: int
    version_id: int
    epic_title: str
    user_code: str
    codemod_context: CodemodContext

    # Sentry tags
    epic_id: int
    is_admin: bool = False


class GroupingConfig(BaseModel):
    subdirectories: list[str] | None = None
    group_by: GroupBy | None = None
    max_prs: int | None = None


class BranchConfig(BaseModel):
    base_branch: str | None = None
    custom_head_branch: str | None = None
    force_push_head_branch: bool = False


class CodemodRunResult(BaseModel):
    is_complete: bool = False
    observation: str | None = None
    visualization: dict | None = None
    observation_meta: dict | None = None
    base_commit: str | None = None
    logs: str | None = None
    error: str | None = None
    completed_at: datetime | None = None
    highlighted_diff: str | None = None
    pr_options: PROptions | None = None
    flags: list[dict] | None = None


class CreatedBranch(BaseModel):
    base_branch: str
    head_ref: str | None = None


class SandboxRunnerTag(BaseModel):
    repo_id: str
    runner_id: str
