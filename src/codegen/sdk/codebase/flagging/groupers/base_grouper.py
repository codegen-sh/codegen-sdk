from codegen.git.repo_operator.remote_repo_operator import RemoteRepoOperator
from codegen.sdk.codebase.flagging.code_flag import CodeFlag
from codegen.sdk.codebase.flagging.group import Group
from codegen.sdk.codebase.flagging.groupers.enums import GroupBy


class BaseGrouper:
    """Base class of all groupers.
    Children of this class should include in their doc string:
        - a short desc of what the segment format is. ex: for FileGrouper the segment is a filename
    """

    type: GroupBy

    def __init__(self) -> None:
        if type is None:
            raise ValueError("Must set type in BaseGrouper")

    @staticmethod
    def create_all_groups(flags: list[CodeFlag], repo_operator: RemoteRepoOperator | None = None) -> list[Group]:
        raise NotImplementedError("Must implement create_all_groups in BaseGrouper")

    @staticmethod
    def create_single_group(flags: list[CodeFlag], segment: str, repo_operator: RemoteRepoOperator | None = None) -> Group:
        """TODO: handle the case when 0 flags are passed in"""
        raise NotImplementedError("Must implement create_single_group in BaseGrouper")
