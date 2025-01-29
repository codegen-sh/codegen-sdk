from codegen.sdk.core.codebase import Codebase
from codemods.codemod import Codemod


def test_codemod_execute() -> None:
    def sample_execute(codebase: Codebase) -> None:
        for file in codebase.files:
            file.content = "print('hello')"

    codemod = Codemod(name="sample_codemod", execute=sample_execute)
    assert id(codemod.execute) == id(sample_execute)

    codemod = Codemod(name="sample_codemod")
    assert codemod.execute is None
