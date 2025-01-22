from graph_sitter.codemod import Codemod3
from graph_sitter.core.codebase import Codebase
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.enums import ProgrammingLanguage
from graph_sitter.skills.core.skill import Skill
from graph_sitter.skills.core.utils import skill, skill_impl
from graph_sitter.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a Python codemod that iterates through all functions in the `app` directory of a codebase. For each function that is not private and is not
being imported anywhere, rename it to be internal by prefixing its name with an underscore. Ensure that the function checks the file path to confirm
it belongs to the `app` directory and uses a method to find import usages.""",
    uid="cb5c6f1d-0a00-46e3-ac0d-c540ab665041",
)
@canonical
class MarkInternalToModule(Codemod3, Skill):
    """This codemod looks at all functions in the `app` directory and marks them as internal if they are not being imported anywhere"""

    language = ProgrammingLanguage.PYTHON

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.PYTHON)
    def execute(self, codebase: Codebase) -> None:
        for function in codebase.functions:
            if "app" in function.file.filepath:
                # Check if the function is not internal
                if not function.is_private and function.name is not None:
                    # Check if the function is not being imported anywhere
                    if not any(usage.kind in (UsageKind.IMPORTED, UsageKind.IMPORTED_WILDCARD) for usage in function.usages):
                        # Rename the function to be internal
                        function.rename("_" + function.name)
