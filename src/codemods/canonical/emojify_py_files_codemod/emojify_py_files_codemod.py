from graph_sitter.codemod import Codemod3
from graph_sitter.core.codebase import Codebase
from graph_sitter.enums import ProgrammingLanguage
from graph_sitter.skills.core.skill import Skill
from graph_sitter.skills.core.utils import skill, skill_impl
from graph_sitter.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a Python codemod that iterates over all Python files in a codebase and adds a rainbow emoji comment at the beginning of each file. The
codemod should be implemented in the `execute` function of the `EmojifyPyFilesCodemod` class, which inherits from `Codemod3` and `Skill`. Ensure that
the new content for each file starts with the comment '#ð' followed by the original content of the file.""",
    uid="5d8f1994-7f74-42e8-aaa8-0c41ced228ef",
)
@canonical
class EmojifyPyFilesCodemod(Codemod3, Skill):
    """Trivial codemod to add a rainbow emoji in a comment at the beginning of all Python files."""

    language = ProgrammingLanguage.PYTHON

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.PYTHON)
    def execute(self, codebase: Codebase) -> None:
        # iterate over files
        for file in codebase.files:
            # add the rainbow emoji to the top of the file
            new_content = "#🌈" + "\n" + file.content
            file.edit(new_content)
