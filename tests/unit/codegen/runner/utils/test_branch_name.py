from unittest.mock import MagicMock

from codegen.runner.utils.branch_name import get_head_branch_name


def test_get_head_branch_name_no_name():
    branch_name = get_head_branch_name(branch_name=None, group=None)
    assert branch_name.startswith("codegen-")


def test_get_head_branch_name_with_name():
    branch_name = get_head_branch_name(branch_name="test", group=None)
    assert branch_name == "test"


def test_get_head_branch_name_with_group():
    group = MagicMock(id=2)
    branch_name = get_head_branch_name(branch_name=None, group=group)
    assert branch_name.startswith("codegen-")
    assert branch_name.endswith("group-2")


def test_get_head_branch_name_with_name_and_group():
    group = MagicMock(id=2)
    branch_name = get_head_branch_name(branch_name="test", group=group)
    assert branch_name == "test-group-2"
