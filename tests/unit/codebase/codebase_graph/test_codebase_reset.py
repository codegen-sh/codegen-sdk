import pytest

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.codebase import Codebase
from codegen.sdk.enums import ProgrammingLanguage


@pytest.fixture
def original(request):
    return request.param


@pytest.fixture
def expected(request):
    return request.param


@pytest.fixture
def programming_language(request):
    return request.param


@pytest.fixture
def codebase(tmp_path, original: dict[str, str], expected: dict[str, str], programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON):
    with get_codebase_session(files=original, programming_language=programming_language, tmpdir=tmp_path) as codebase:
        yield codebase
    if expected is not None:
        for file in expected:
            assert codebase.get_file(file).content.strip() == expected[file].strip()
            assert tmp_path.joinpath(file).exists()
            assert tmp_path.joinpath(file).read_text() == expected[file]
        for file in codebase.files:
            assert file.filepath in expected


@pytest.mark.parametrize(
    "original, expected",
    [
        ({"a.py": "a"}, {"a.py": "a"}),
        ({"a.py": "a", "b.py": "b"}, {"a.py": "a", "b.py": "b"}),
        ({"a.py": "a", "b.py": "b"}, {"a.py": "a", "b.py": "b"}),
    ],
    indirect=["original", "expected"],
)
def test_codebase_reset(codebase: Codebase):
    codebase.get_file("a.py").edit("b")
    codebase.reset()
