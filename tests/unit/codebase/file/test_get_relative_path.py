from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_get_relative_path_same_directory(tmpdir) -> None:
    # Prepare the files for this test
    files = {
        "src/file1.py": "print('file1')",
        "src/file2.js": "console.log('file2')",
    }

    with get_codebase_session(tmpdir=tmpdir, files=files) as codebase:
        relative = codebase.get_relative_path("src/file1.py", "src/file2.js")
        assert relative == "file2", f"Expected 'file2' but got {relative!r}"


def test_get_relative_path_subdirectory(tmpdir) -> None:
    files = {
        "src/file1.py": "print('file1')",
        "src/subdir/file2.js": "console.log('file2')",
    }

    with get_codebase_session(tmpdir=tmpdir, files=files) as codebase:
        relative = codebase.get_relative_path("src/file1.py", "src/subdir/file2.js")
        assert relative == "subdir/file2", f"Expected 'subdir/file2' but got {relative!r}"


def test_get_relative_path_move_up_one_directory(tmpdir) -> None:
    files = {
        "src/subdir/file1.py": "print('file1')",
        "src/file2.ts": "console.log('file2')",
    }

    with get_codebase_session(tmpdir=tmpdir, files=files) as codebase:
        relative = codebase.get_relative_path("src/subdir/file1.py", "src/file2.ts")
        assert relative == "../file2", f"Expected '../file2' but got {relative!r}"


def test_get_relative_path_different_folders_deep(tmpdir) -> None:
    files = {
        "src/subdir/deeper/file1.ts": "console.log('file1')",
        "src/subdir/file2.tsx": "console.log('file2')",
    }

    with get_codebase_session(tmpdir=tmpdir, files=files) as codebase:
        relative = codebase.get_relative_path("src/subdir/deeper/file1.ts", "src/subdir/file2.tsx")
        assert relative == "../file2", f"Expected '../file2' but got {relative!r}"


def test_get_relative_path_multiple_levels_up(tmpdir) -> None:
    files = {
        "src/subdir/deeper/file1.ts": "console.log('file1')",
        "tests/file2.js": "console.log('file2')",
    }

    with get_codebase_session(tmpdir=tmpdir, files=files) as codebase:
        relative = codebase.get_relative_path("src/subdir/deeper/file1.ts", "tests/file2.js")
        assert relative == "../../../tests/file2", f"Expected '../../../tests/file2' but got {relative!r}"


def test_get_relative_path_same_file(tmpdir) -> None:
    files = {
        "src/subdir/deeper/file.ts": "console.log('file')",
    }

    with get_codebase_session(tmpdir=tmpdir, files=files) as codebase:
        relative = codebase.get_relative_path("src/subdir/deeper/file.ts", "src/subdir/deeper/file.ts")
        assert relative == "file", f"Expected 'file' but got {relative!r}"
