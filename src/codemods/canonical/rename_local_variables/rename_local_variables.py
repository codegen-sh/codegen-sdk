from codegen_sdk.codemod import Codemod3
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.skills.core.skill import Skill
from codegen_sdk.skills.core.utils import skill, skill_impl
from codegen_sdk.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a Python codemod that iterates through a codebase, identifying functions with local variables containing the name 'position'. For each
identified function, rename all occurrences of the local variable 'position' to 'pos', ensuring that the renaming is applied to all relevant usages
within the function.""",
    uid="79c10c00-bbce-4bdb-8c39-d91586307a2b",
)
@canonical
class RenameLocalVariables(Codemod3, Skill):
    """This codemod renames all local variables in functions that contain 'position' to 'pos'

    Example:
    Before:
    ```
        def some_function(x, y, position):
            position_x = x + position
            position_y = y + position
            return position_x, position_y
    ```
    After:
    ```
        def some_function(x, y, position):
            pos_x = x + position
            pos_y = y + position
            return pos_x, pos_y
    ```
    """

    language = ProgrammingLanguage.PYTHON

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.PYTHON)
    def execute(self, codebase: Codebase) -> None:
        # iterate over files
        for file in codebase.files:
            for function in file.functions:
                # Check if any local variable names contain "position"
                business_vendor_usages = function.code_block.get_variable_usages("position", fuzzy_match=True)
                if len(business_vendor_usages) > 0:
                    # Rename
                    function.rename_local_variable("position", "pos", fuzzy_match=True)
