from codegen.sdk.codemod import Codemod3
from codegen.sdk.core.codebase import Codebase
from codegen.sdk.enums import ProgrammingLanguage
from codegen.sdk.skills.core.skill import Skill
from codegen.sdk.skills.core.utils import skill, skill_impl
from codegen.sdk.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a TypeScript codemod that iterates through a codebase, identifies JSX functions, and replaces any occurrences of the prop value 'text-center'
with 'text-left' in all JSX elements.""",
    uid="c1914552-556b-4ae0-99f0-33cb7bfb702e",
)
@canonical
class ReplacePropValues(Codemod3, Skill):
    """Replaces any JSX props with text-center to text-left"""

    language = ProgrammingLanguage.TYPESCRIPT

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.TYPESCRIPT)
    def execute(self, codebase: Codebase) -> None:
        # Iterate over all files in the codebase
        for file in codebase.files:
            # Iterate over all functions in the file
            for function in file.functions:
                # Filter for JSX functions
                if function.is_jsx:
                    # Iterate over all JSX elements in the function
                    for jsx_element in function.jsx_elements:
                        # Iterate over all the props of the component
                        for prop in jsx_element.props:
                            # Check if prop has a value
                            if prop.value:
                                # Replace text-center with text-left
                                prop.value.replace("text-center", "text-left")
