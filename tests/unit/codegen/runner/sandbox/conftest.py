from collections.abc import Generator
from unittest.mock import patch

import pytest

from codegen.git.repo_operator.local_repo_operator import LocalRepoOperator
from codegen.runner.models.configs import RunnerFeatureFlags
from codegen.runner.sandbox.executor import SandboxExecutor
from codegen.runner.sandbox.runner import SandboxRunner
from codegen.sdk.codebase.config import CodebaseConfig, GSFeatureFlags, ProjectConfig
from codegen.sdk.core.codebase import Codebase
from codegen.sdk.secrets import Secrets
from codegen.shared.enums.programming_language import ProgrammingLanguage


@pytest.fixture
def codebase(tmpdir) -> Codebase:
    op = LocalRepoOperator.create_from_files(repo_path=f"{tmpdir}/test-repo", files={"test.py": "a = 1"}, bot_commit=True)
    projects = [ProjectConfig(repo_operator=op, programming_language=ProgrammingLanguage.PYTHON)]
    codebase = Codebase(projects=projects)
    return codebase


@pytest.fixture
def executor(codebase: Codebase) -> Generator[SandboxExecutor]:
    yield SandboxExecutor(codebase)


@pytest.fixture
def runner(codebase: Codebase, tmpdir):
    with patch("codegen.runner.sandbox.runner.RemoteRepoOperator") as mock_op:
        with patch.object(SandboxRunner, "_build_graph") as mock_init_codebase:
            mock_init_codebase.return_value = codebase
            mock_op.return_value = codebase.op

            yield SandboxRunner(repo_config=codebase.op.repo_config)


@pytest.fixture(autouse=True)
def mock_codebase_config():
    with patch("codegen.runner.sandbox.runner.get_codebase_config") as mock_config:
        gs_ffs = GSFeatureFlags(**RunnerFeatureFlags().model_dump())
        secrets = Secrets(openai_key="test-key")
        mock_config.return_value = CodebaseConfig(secrets=secrets, feature_flags=gs_ffs)
        yield mock_config
