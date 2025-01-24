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
def codebase(tmp_path, original: dict[str, str], programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON):
    with get_codebase_session(files=original, programming_language=programming_language, tmpdir=tmp_path) as codebase:
        yield codebase


@pytest.fixture
def assert_expected(expected: dict[str, str], tmp_path):
    def assert_expected(codebase: Codebase):
        codebase.commit()
        for file in expected:
            assert tmp_path.joinpath(file).exists()
            assert tmp_path.joinpath(file).read_text() == expected[file]
            assert codebase.get_file(file).content.strip() == expected[file].strip()
        for file in codebase.files:
            assert file.filepath in expected

    return assert_expected


@pytest.mark.parametrize(
    "original, expected",
    [
        ({"a.py": "a"}, {"a.py": "a"}),
        ({"a.py": "a", "b.py": "b"}, {"a.py": "a", "b.py": "b"}),
    ],
    indirect=["original", "expected"],
)
def test_codebase_reset(codebase: Codebase, assert_expected):
    codebase.get_file("a.py").edit("b")
    codebase.reset()
    assert_expected(codebase)


@pytest.mark.parametrize(
    "original, expected",
    [
        ({"a.py": "a"}, {"a.py": "b"}),
    ],
    indirect=["original", "expected"],
)
def test_codebase_reset_external_changes(codebase: Codebase, assert_expected):
    codebase.get_file("a.py").path.write_text("b")
    codebase.reset()
    assert_expected(codebase)


@pytest.mark.parametrize(
    "original, expected",
    [
        ({"a.py": "a"}, {"a.py": "a"}),
    ],
    indirect=["original", "expected"],
)
def test_codebase_reset_manual_file_add(codebase: Codebase, assert_expected, tmp_path):
    # Manually create a new file
    new_file = tmp_path / "new.py"
    new_file.write_text("new content")
    codebase.reset()
    assert_expected(codebase)


@pytest.mark.parametrize(
    "original, expected",
    [
        ({"a.py": "a", "b.py": "b"}, {"a.py": "a", "b.py": "b"}),
    ],
    indirect=["original", "expected"],
)
def test_codebase_reset_manual_file_delete(codebase: Codebase, assert_expected):
    # Manually delete a file
    codebase.get_file("b.py").path.unlink()
    codebase.reset()
    assert_expected(codebase)


@pytest.mark.parametrize(
    "original, expected",
    [
        ({"old.py": "content"}, {"old.py": "content"}),
    ],
    indirect=["original", "expected"],
)
def test_codebase_reset_manual_file_rename(codebase: Codebase, tmp_path, assert_expected):
    # Manually rename a file
    old_path = codebase.get_file("old.py").path
    new_path = tmp_path / "new.py"
    old_path.rename(new_path)
    codebase.reset()
    assert_expected(codebase)
