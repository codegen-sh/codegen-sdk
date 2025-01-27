from pathlib import Path

import pytest

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.enums import ProgrammingLanguage


def generate_files(num_files: int, extension: str = "py") -> dict[str, str]:
    return {f"file{i}.{extension}": f"# comment {i}" for i in range(num_files)}


cases = [10**i for i in range(1, 4)]


@pytest.mark.timeout(5, func_only=True)
@pytest.mark.parametrize("extension, num_files", [(ext, i) for ext in ["txt", "py"] for i in cases])
def test_codebase_reset_stress_test(extension: str, num_files: int, tmp_path):
    files = generate_files(num_files, extension)
    with get_codebase_session(files=files, programming_language=ProgrammingLanguage.PYTHON, tmpdir=Path(tmp_path), sync_graph=False) as codebase:
        for file in files:
            codebase.get_file(file).edit(f"# comment2 {file}")
    codebase.reset()
    for file, original_content in files.items():
        assert (tmp_path / file).exists()
        assert (tmp_path / file).read_text() == original_content
