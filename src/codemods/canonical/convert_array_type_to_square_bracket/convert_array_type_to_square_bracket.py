from codegen_sdk.codemod import Codemod3
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.core.expressions.generic_type import GenericType
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.skills.core.skill import Skill
from codegen_sdk.skills.core.utils import skill, skill_impl
from codegen_sdk.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a TypeScript codemod that converts types from `Array<T>` to `T[]`. The codemod should iterate through all files in a codebase, checking each
function's return type and parameters. If a return type or parameter type is of the form `Array<T>`, it should be transformed to `T[]`. Ensure that the
codemod handles edge cases, such as nested Array types, appropriately.""",
    uid="97184a15-5992-405b-be7b-30122556fe8b",
)
@canonical
class ConvertArrayTypeToSquareBracket(Codemod3, Skill):
    """This codemod converts types of the form `Array<T>` to `T[]`, while avoiding edge cases like nested Array types"""

    language = ProgrammingLanguage.TYPESCRIPT

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.TYPESCRIPT)
    def execute(self, codebase: Codebase) -> None:
        # Iterate over all files in the codebase
        for file in codebase.files:
            # Iterate over all functions in the file
            for func in file.functions:
                # Check if the return type is of the form Array<T>
                if (return_type := func.return_type) and isinstance(return_type, GenericType) and return_type.name == "Array":
                    # Array<..> syntax only allows one type argument
                    func.set_return_type(f"({return_type.parameters[0].source})[]")

                # Process each parameter in the function
                for param in func.parameters:
                    if (param_type := param.type) and isinstance(param_type, GenericType) and param_type.name == "Array":
                        # Array<..> syntax only allows one type argument
                        param_type.edit(f"({param_type.parameters[0].source})[]")
