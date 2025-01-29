import codegen
from codegen import Codebase


def test_codegen_imports() -> None:
    # Test decorated function
    @codegen.function(name="sample_codemod")
    def run(codebase) -> None:
        pass

    # Test class
    cls = codegen.Function
    assert cls is not None

    codebase = Codebase("./")
    assert codebase is not None
