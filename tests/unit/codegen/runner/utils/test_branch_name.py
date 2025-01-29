from unittest.mock import MagicMock

from codegen.runner.utils.branch_name import get_head_branch_name


def test_get_head_branch_name_no_group() -> None:
    codemod = MagicMock(epic_id=123, version_id=456, run_id=789)
    branch_name = get_head_branch_name(codemod=codemod, group=None)
    assert branch_name == "codegen-codemod-123-version-456-run-789-group-0"


def test_get_head_branch_name_with_group() -> None:
    codemod = MagicMock(epic_id=123, version_id=456, run_id=789)
    group = MagicMock(id=2)
    branch_name = get_head_branch_name(codemod=codemod, group=group)
    assert branch_name == "codegen-codemod-123-version-456-run-789-group-2"
