from codegen_sdk.codemod import Codemod3
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.skills.core.skill import Skill
from codegen_sdk.skills.core.utils import skill, skill_impl
from codegen_sdk.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a Python codemod that wraps the code blocks of all internally marked functions (those starting with an underscore) in a codebase with a
'with' statement using 'before_execute() as before'. The codemod should iterate through all Python files in the codebase and apply the wrapping to the
relevant functions.""",
    uid="345deafc-ac72-4537-8d13-ff27ac6e67f1",
)
@canonical
class WrapWithStatement(Codemod3, Skill):
    """Wraps code blocks (that meet certain criteria) with a with statement.

    Before:

        def _table_name_from_select_element(elt):
            t = elt.forms[0]
            return t.name

    After:

        def _table_name_from_select_element(elt):
            with before_execute() as before:
                t = elt.forms[0]
                return t.name
    """

    language = ProgrammingLanguage.PYTHON

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.PYTHON)
    def execute(self, codebase: Codebase) -> None:
        # Iterate over all Python files in the codebase
        for file in codebase.files:
            # Search for specific function calls that need to be refactored
            for function in file.functions:
                # Find any internally marked function
                if function.name.startswith("_"):
                    function.code_block.wrap(before_src="with before_execute() as before:")
