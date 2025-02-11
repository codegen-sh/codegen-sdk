import uuid

import pytest

from codegen.sdk.core.codebase import Codebase


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
