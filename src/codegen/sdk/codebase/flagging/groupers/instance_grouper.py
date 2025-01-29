from __future__ import annotations

from typing import TYPE_CHECKING

from codegen.sdk.codebase.flagging.code_flag import CodeFlag
from codegen.sdk.codebase.flagging.group import Group
from codegen.sdk.codebase.flagging.groupers.base_grouper import BaseGrouper
from codegen.sdk.codebase.flagging.groupers.enums import GroupBy

if TYPE_CHECKING:
    from codegen.git.repo_operator.remote_repo_operator import RemoteRepoOperator


class InstanceGrouper(BaseGrouper):
    """Group flags by flags. haha
    One Group per flag.
    """

    type: GroupBy = GroupBy.INSTANCE

    @staticmethod
    def create_all_groups(flags: list[CodeFlag], repo_operator: RemoteRepoOperator | None = None) -> list[Group]:
        return [Group(id=idx, group_by=GroupBy.INSTANCE, segment=f.hash, flags=[f]) for idx, f in enumerate(flags)]

    @staticmethod
    def create_single_group(flags: list[CodeFlag], segment: str, repo_operator: RemoteRepoOperator | None = None) -> Group:
        # TODO: not sure if it's possible to regenerate a group for instance grouper b/c it needs to re-generate/re-find the flag. might need to rely on the flag meta 🤦‍♀️
        try:
            flag = CodeFlag.from_json(segment)
            return Group(group_by=GroupBy.INSTANCE, segment=segment, flags=[flag])
        except Exception:
            msg = f"Unable to deserialize segment ({segment}) into CodeFlag. Unable to create group."
            raise ValueError(msg)
