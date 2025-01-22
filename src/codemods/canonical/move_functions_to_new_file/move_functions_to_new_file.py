from codegen_sdk.codemod import Codemod3
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.core.file import SourceFile
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.skills.core.skill import Skill
from codegen_sdk.skills.core.utils import skill, skill_impl
from codegen_sdk.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a Python codemod that moves all functions starting with 'pylsp_' from existing files in a codebase to a new file named 'pylsp_shared.py'.
Ensure that all imports across the codebase are updated to reflect the new location of these functions. The codemod should iterate through each file
in the codebase, create the new file, and move the matching functions while including their dependencies.""",
    uid="b29f6b8b-0837-4548-b770-b597bbcd3e02",
)
@canonical
class MoveFunctionsToNewFile(Codemod3, Skill):
    """This codemod moves functions that starts with "pylsp_" in their names to a new file called pylsp_shared.py

    When it moves them to this file, all imports across the codebase will get updated to reflect the new location.
    """

    language = ProgrammingLanguage.PYTHON

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.PYTHON)
    def execute(self, codebase: Codebase):
        # Create a new file for storing the functions that contain pylsp util functions
        new_file: SourceFile = codebase.create_file("pylsp/pylsp_shared.py", "")
        for file in codebase.files:
            # Move function's name contains 'pylsp_' as a prefix
            for function in file.functions:
                if function.name.startswith("pylsp_"):
                    # Move each function that matches the criteria to the new file
                    function.move_to_file(new_file, include_dependencies=True, strategy="update_all_imports")
