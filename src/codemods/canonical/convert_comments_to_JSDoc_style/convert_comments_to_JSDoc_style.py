from codegen.sdk.codemod import Codemod3
from codegen.sdk.core.codebase import Codebase
from codegen.sdk.enums import ProgrammingLanguage
from codegen.sdk.skills.core.skill import Skill
from codegen.sdk.skills.core.utils import skill, skill_impl
from codegen.sdk.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a codemod that converts comments on exported functions and classes in a TypeScript codebase to JSDoc style. The codemod should iterate
through all functions and classes, check if they are exported, and if they lack docstrings. If comments are present and do not contain 'eslint',
escape any occurrences of '*/' in the comments to prevent breaking the JSDoc block, then convert the comments to JSDoc format. Finally, remove the
original comments after conversion.""",
    uid="846a3894-b534-4de2-9810-94bc691a5687",
)
@canonical
class ConvertCommentsToJSDocStyle(Codemod3, Skill):
    """This codemod converts the comments on any exported function or class to JSDoc style if they aren't already in JSDoc style.

    A JSDoc style comment is one that uses /** */ instead of //

    It also accounts for some common edgecases like avoiding eslint comments or comments which include a */ in them that needs to be escaped
    """

    language = ProgrammingLanguage.TYPESCRIPT

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.TYPESCRIPT)
    def execute(self, codebase: Codebase) -> None:
        # Iterate over all functions and classes in the codebase
        for symbol in codebase.functions + codebase.classes:
            # Check if the symbol is exported
            if symbol.is_exported:
                # Check if the symbol is missing docstrings
                if not symbol.docstring:
                    # Check if the symbol has comments
                    if symbol.comment:
                        # If eslint comments are present, skip conversion
                        if "eslint" not in symbol.comment.text:
                            # Escape any `*/` found in the comment to prevent breaking the JSDoc block
                            escaped_comment = symbol.comment.text.replace("*/", r"*\/")
                            # Convert comment to JSdoc docstrings
                            # symbol.set_docstring(escaped_comment, force_multiline=True)
                            symbol.set_docstring(escaped_comment, force_multiline=True)
                            symbol.comment.remove()
