import re

from codegen.runner.models.codemod import Codemod
from codegen.sdk.codebase.flagging.group import DEFAULT_GROUP_ID, Group

# Codegen branches are of the format: codegen-codemod-<epic_id>-version-<codemod_version_id>-run-<cm_run_id>-group-<group_id>
CODEGEN_BRANCH_PATTERN = r"codegen-codemod-(\d+)-version-(\d+)-run-(\d+)-group-(\d+)"

# Regex used for parsing DB IDs from Codegen branch names
CODEGEN_BRANCH_REGEX = re.compile(f"^{CODEGEN_BRANCH_PATTERN}$")

# Template used to create a Codegen branch name
CODEGEN_BRANCH_TEMPLATE = CODEGEN_BRANCH_PATTERN.replace("(\\d+)", "{}")


def get_head_branch_name(codemod: Codemod, group: Group | None = None) -> str:
    if not codemod.version_id:
        msg = f"CodemodRun: {codemod.run_id} does not have a codemod version!"
        raise ValueError(msg)
    if not codemod.epic_id:
        msg = f"CodemodRun: {codemod.run_id} does not have an epic!"
        raise ValueError(msg)
    if group and group.id is None:
        msg = "Group ID is required to create a branch name"
        raise ValueError(msg)

    group_id = group.id if group else DEFAULT_GROUP_ID
    return CODEGEN_BRANCH_TEMPLATE.format(codemod.epic_id, codemod.version_id, codemod.run_id, group_id)
