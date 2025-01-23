from graph_sitter.core.codebase import Codebase
from graph_sitter.testing.test_utils import codemod_test


def add_rainbow(codebase: Codebase) -> None:
    """Add a rainbow emoji to the README."""
    # Find the README file
    file = codebase.get_file("README.md")
    file.edit("# 🌈 Kevin's Adventure Game")
    codebase.commit()


@codemod_test("codegen-sh/Kevin-s-Adventure-Game")
def test_add_rainbow(codebase: Codebase) -> None:
    """Test adding a rainbow emoji to README."""
    add_rainbow(codebase)
    assert codebase.get_file("README.md").lines[0].source == "# 🌈 Kevin's Adventure Game"
