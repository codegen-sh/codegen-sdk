from unittest.mock import MagicMock

from codegen.sdk.codebase.flagging.code_flag import CodeFlag, MessageType
from codegen.sdk.codebase.flagging.groupers.all_grouper import AllGrouper


def test_group_all():
    flag1 = CodeFlag(
        symbol=MagicMock(
            file=MagicMock(filepath="test.py"),
            node_id="12345",
        ),
        message="test message",
        message_type=MessageType.GITHUB,
        message_recipient="12345",
    )
    flag2 = CodeFlag(
        symbol=MagicMock(
            file=MagicMock(filepath="test.py"),
            node_id="12345",
        ),
        message="test message",
        message_type=MessageType.GITHUB,
        message_recipient="12345",
    )
    flags = [flag1, flag2]
    groups = AllGrouper.create_all_groups(flags)
    assert len(groups) == 1
    assert len(groups[0].flags) == 2
    assert groups[0].flags[0] == flag1
    assert groups[0].flags[1] == flag2
