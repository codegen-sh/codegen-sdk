from codegen_sdk.codemod import Codemod3
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.skills.core.skill import Skill
from codegen_sdk.skills.core.utils import skill, skill_impl
from codegen_sdk.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a Python codemod that iterates through all files in a codebase, identifies function parameters containing the substring 'obj', and renames
them to 'new_obj'. The codemod should be structured as a class that inherits from Codemod3 and Skill, with an execute method that performs the
renaming operation.""",
    uid="1576b2fd-8a00-44e4-9659-eb0f585e015a",
)
@canonical
class RenameFunctionParameters(Codemod3, Skill):
    """This takes all functions that renames any parameter that contains 'obj' and replaces with 'new_obj'"""

    language = ProgrammingLanguage.PYTHON

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.PYTHON)
    def execute(self, codebase: Codebase) -> None:
        # Iterate over all files
        for file in codebase.files:
            for function in file.functions:
                # Search for parameter names that contain 'obj'
                params_to_rename = [p for p in function.parameters if "obj" in p.name]
                if params_to_rename:
                    # Rename the parameters
                    for param in params_to_rename:
                        new_param_name = param.name.replace("obj", "new_obj")
                        param.rename(new_param_name)
