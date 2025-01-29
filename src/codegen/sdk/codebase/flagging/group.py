from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from dataclasses_json import dataclass_json

if TYPE_CHECKING:
    from codegen.sdk.codebase.flagging.code_flag import CodeFlag
    from codegen.sdk.codebase.flagging.groupers.enums import GroupBy

DEFAULT_GROUP_ID = 0


@dataclass_json
@dataclass
class Group:
    group_by: GroupBy
    segment: str
    flags: list[CodeFlag] | None = None
    id: int = DEFAULT_GROUP_ID
