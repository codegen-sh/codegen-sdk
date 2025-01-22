from codegen_sdk.codemod import Codemod3
from codegen_sdk.core.class_definition import Class
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.core.interface import Interface
from codegen_sdk.core.type_alias import TypeAlias
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.skills.core.skill import Skill
from codegen_sdk.skills.core.utils import skill, skill_impl
from codegen_sdk.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a TypeScript codemod that converts all Classes, Interfaces, and Types in a codebase to PascalCase. The codemod should iterate through all
symbols in the codebase, check if each symbol is a Class, Interface, or Type using the `isinstance` function, and if the symbol's name is not
capitalized, it should convert the name to PascalCase by capitalizing the first letter of each word and removing underscores. Finally, the codemod
should rename the symbol and update all references accordingly.""",
    uid="bbb9e26a-7911-4b94-a4eb-207b9d32d18f",
)
@canonical
class PascalCaseSymbols(Codemod3, Skill):
    """This (Typescript) codemod converts all Classes, Interfaces and Types to be in PascalCase using simple logic.

    Note the use of the `isinstance(symbol, (Class | Interface | Type))` syntax to check if the symbol is a Class, Interface, or Type.
    You should always use the abstract base class to check for the type of a symbol.
    """

    language = ProgrammingLanguage.TYPESCRIPT

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.TYPESCRIPT)
    def execute(self, codebase: Codebase) -> None:
        # Iterate over all symbols in the codebase
        for symbol in codebase.symbols:
            # Check if the symbol is a Class, Interface, or Type with `isinstance` syntax
            if isinstance(symbol, (Class | Interface | TypeAlias)):
                # Check if the name isn't capitalized
                if not symbol.name[0].isupper():
                    # Generate the PascalCase name
                    new_name = "".join(word.capitalize() for word in symbol.name.replace("_", " ").split())
                    # Rename the symbol and update all references
                    symbol.rename(new_name)
