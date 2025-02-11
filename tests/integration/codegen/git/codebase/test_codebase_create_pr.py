import uuid

import pytest

from codegen.git.repo_operator.local_repo_operator import LocalRepoOperator
from codegen.git.utils.clone import clone_repo
from codegen.git.utils.clone_url import get_authenticated_clone_url_for_repo_config
from codegen.sdk.codebase.config import ProjectConfig
from codegen.sdk.core.codebase import Codebase
from codegen.shared.configs.config import config


@pytest.fixture
def op(repo_config, tmpdir):
    clone_repo(repo_path=f"{tmpdir}/{repo_config.name}", clone_url=get_authenticated_clone_url_for_repo_config(repo_config, token=config.secrets.github_token))
    op = LocalRepoOperator(repo_config=repo_config, github_api_key=config.secrets.github_token)
    yield op


@pytest.fixture
def codebase(op: LocalRepoOperator):
    project_config = ProjectConfig(repo_operator=op)
    codebase = Codebase(projects=[project_config])
    yield codebase


def test_codebase_create_pr_active_branch(codebase: Codebase):
    head = f"test-create-pr-{uuid.uuid4()}"
    codebase.checkout(branch=head, create_if_missing=True)
    codebase.files[0].remove()
    codebase.commit()
    pr = codebase.create_pr(title="test-create-pr title", body="test-create-pr body")
    assert pr.title == "test-create-pr title"
    assert pr.body == "test-create-pr body"
    assert pr.draft is False
    assert pr.state == "open"
    assert pr.head.ref == head
    assert pr.base.ref == "main"


def test_codebase_create_pr_detached_head(codebase: Codebase):
    codebase.checkout(commit=codebase._op.git_cli.head.commit)  # move to detached head state
    with pytest.raises(ValueError) as exc_info:
        codebase.create_pr(title="test-create-pr title", body="test-create-pr body")
    assert "Cannot make a PR from a detached HEAD" in str(exc_info.value)
