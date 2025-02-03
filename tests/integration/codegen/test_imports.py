import codegen
from codegen import Codebase
from codegen.sdk.code_generation.current_code_codebase import get_codegen_codebase_base_path


def test_codegen_imports():
    # Test decorated function
    @codegen.function(name="sample_codemod")
    def run(codebase):
        pass

    # Test class
    cls = codegen.Function
    assert cls is not None
    codebase = Codebase(get_codegen_codebase_base_path())
    assert codebase is not None
