from graph_sitter.codemod import Codemod3
from graph_sitter.core.codebase import Codebase
from graph_sitter.enums import ProgrammingLanguage
from graph_sitter.skills.core.skill import Skill
from graph_sitter.skills.core.utils import skill, skill_impl
from graph_sitter.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a Python codemod that transforms a single decorator call into multiple calls. The codemod should iterate through all classes in a codebase,
identify decorators matching the pattern '@generic_repr', and replace them with separate decorators for each argument passed to the original
decorator. Ensure that the original decorator's ordering is preserved by editing in-place.""",
    uid="3f6325b8-02c3-4d90-a726-830f8bccce3a",
)
@canonical
class SplitDecorators(Codemod3, Skill):
    """This codemod splits a single decorator call into multiple

    For example:
        @generic_repr("id", "name", "email")
        def f():
            ...

    Becomes:
        @generic_repr("id")
        @generic_repr("name")
        @generic_repr("email")
        def f():
            ...

    Note that we edit the original decorator in-place (`decorator.edit(...)`), so as to keep the original decorator's ordering!

    If we instead did `add_decorator` etc., we would have to figure out where to insert the new decorators.
    """

    language = ProgrammingLanguage.PYTHON

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.PYTHON)
    def execute(self, codebase: Codebase) -> None:
        # Iterate over all classes in the codebase
        for cls in codebase.classes:
            # Find all decorators of the function that match the pattern for `@allow_update` - this is a list of Decorator instances with '{' in the source
            target_decorators = [decorator for decorator in cls.decorators if "@generic_repr" in decorator.source]
            for decorator in target_decorators:
                new_decorators = []
                for arg in decorator.call.args:
                    new_decorator_source = f"@generic_repr({arg})"
                    new_decorators.append(new_decorator_source)

                # Remove the original decorator as it will be replaced
                decorator.edit("\n".join(new_decorators), fix_indentation=True)
