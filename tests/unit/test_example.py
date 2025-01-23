from graph_sitter.codebase import Codebase
from graph_sitter.testing.test_utils import test_case


@test_case(repos=["facebook/react"])
def run(codebase: Codebase) -> None:
    """Example test case that runs against the React codebase."""
    # Find all function declarations
    functions = list(codebase.functions)

    # Assert we found some functions
    assert len(functions) > 0, "Expected to find functions in React codebase"

    # Example: Check that no function is too long (>1000 lines)
    for func in functions:
        assert len(func.source.splitlines()) < 1000, f"Function {func.name} is too long"


def test_react_functions():
    """Test function that runs the test case."""
    run()
