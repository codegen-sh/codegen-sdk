from graph_sitter.core.codebase import Codebase
from graph_sitter.testing.test_utils import test_case


@test_case(repos=["fastapi/fastapi"])
def run(codebase: Codebase) -> None:
    """Test that verifies typing imports can be converted to built-in types."""
    # Find all imports from typing module
    typing_imports = []
    for file in codebase.files:
        for imp in file.imports:
            if imp.module == "typing" and imp.name in ["List", "Dict", "Set", "Tuple"]:
                typing_imports.append(imp)

    # Verify we found some typing imports to convert
    assert len(typing_imports) > 0, "Expected to find typing imports in FastAPI codebase"

    # Verify each import has usages we can convert
    for imp in typing_imports:
        assert len(imp.usages) > 0, f"Expected {imp.name} from typing to have usages"

        # Check that usages can be replaced with built-in types
        for usage in imp.usages:
            # The usage should match the imported name
            assert usage.match.source == imp.name
            # We should be able to edit it to the lowercase version
            new_type = imp.name.lower()
            usage.match.edit(new_type)
            assert usage.match.source == new_type


def test_built_in_type_annotations():
    """Test converting typing imports to built-in types."""
    run()
