from collections.abc import Generator
from unittest.mock import patch

import pytest

from codegen.git.repo_operator.local_repo_operator import LocalRepoOperator
from codegen.git.schemas.repo_config import RepoConfig
from codegen.runner.models.configs import RunnerFeatureFlags
from codegen.runner.sandbox.executor import SandboxExecutor
from codegen.runner.sandbox.runner import SandboxRunner
from codegen.sdk.codebase.config import ProjectConfig
from codegen.sdk.core.codebase import Codebase
from codegen.sdk.enums import ProgrammingLanguage


@pytest.fixture
def codebase(tmpdir, request) -> Codebase:
    repo_id = getattr(request, "param", 1)
    repo_config = RepoConfig(id=repo_id, name="test-repo", full_name="test-org/test-repo", organization_id=1, organization_name="test-org")
    op = LocalRepoOperator.create_from_files(repo_path=tmpdir, files={"test.py": "a = 1"}, bot_commit=True, repo_config=repo_config)
    projects = [ProjectConfig(repo_operator=op, programming_language=ProgrammingLanguage.PYTHON)]
    codebase = Codebase(projects=projects)
    return codebase


@pytest.fixture
def executor(codebase: Codebase) -> Generator[SandboxExecutor]:
    with patch("codegen.runner.sandbox.executor.get_runner_feature_flags") as mock_ff:
        mock_ff.return_value = RunnerFeatureFlags(syntax_highlight=False)

        yield SandboxExecutor(codebase)


@pytest.fixture
def runner(codebase: Codebase, tmpdir):
    with patch("codegen.runner.sandbox.RemoteRepoOperator") as mock_op:
        with patch.object(SandboxRunner, "_build_graph") as mock_init_codebase:
            mock_init_codebase.return_value = codebase
            mock_op.return_value = codebase.op

            yield SandboxRunner(container_id="ta-123", repo_config=codebase.op.repo_config)
