from codegen.sdk.codemod import Codemod3
from codegen.sdk.core.codebase import Codebase
from codegen.sdk.core.external_module import ExternalModule
from codegen.sdk.core.import_resolution import Import
from codegen.sdk.core.symbol import Symbol
from codegen.sdk.enums import ProgrammingLanguage
from codegen.sdk.skills.core.skill import Skill
from codegen.sdk.skills.core.utils import skill, skill_impl
from codegen.sdk.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a Python function named `execute` within a class `RemoveIndirectImports` that processes a codebase to remove all indirect imports. The
function should iterate through all files in the codebase, check each import to determine if it points to another import, and replace it with a direct
import. Handle cases where the resolved import is either an external module or a symbol, ensuring that the import is updated accordingly.""",
    uid="0648c80e-a569-4aa5-b241-38a2dd320e9a",
)
@canonical
class RemoveIndirectImports(Codemod3, Skill):
    """This codemod removes all indirect imports from a codebase (i.e. an import that points to another import),
    replacing them instead with direct imports
    """

    language = ProgrammingLanguage.PYTHON

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.PYTHON)
    def execute(self, codebase: Codebase) -> None:
        # iterate over all files -> imports
        for file in codebase.files:
            for original_import in file.imports:
                # Grab the symbol being imported
                imported_symbol = original_import.imported_symbol

                # Check if the symbol being imported is itself import
                if isinstance(imported_symbol, Import):
                    # We've found an import that points to another import which means it's an indirect import!
                    # Get the symbol that the import eventually resolves to
                    imported_symbol = original_import.resolved_symbol

                    # Case: we can't find the final destination symbol
                    if imported_symbol is None:
                        continue

                    # Case: the resolved import is an external module.
                    elif isinstance(imported_symbol, ExternalModule):
                        original_import.edit(imported_symbol.source)

                    # Case: the resolved import is Symbol.
                    elif isinstance(imported_symbol, Symbol):
                        # Replace the module in the import with the final destination symbol's module
                        # e.g. `from abc import ABC` -> `from xyz import ABC` or equivalent in your language.
                        original_import.set_import_module(imported_symbol.file.import_module_name)
