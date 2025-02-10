from pathlib import Path
from unittest.mock import MagicMock

import pytest

from codegen.sdk.codebase.io.file_io import FileIO
from codegen.sdk.codebase.io.io import FileTracker


@pytest.fixture
def mock_io():
    return MagicMock(spec=FileIO)


@pytest.fixture
def io(mock_io):
    return FileTracker(mock_io)


def test_init_default_io():
    tracker = FileTracker()
    assert isinstance(tracker.io, FileIO)
    assert tracker.pending_files == set()


def test_init_custom_io(mock_io):
    tracker = FileTracker(mock_io)
    assert tracker.io == mock_io
    assert tracker.pending_files == set()


def test_write_file_str(io, mock_io):
    path = Path("test.txt")
    content = "test content"

    io.write_file(path, content)

    assert path in io.pending_files
    mock_io.write_text.assert_called_once_with(path, content)


def test_write_file_bytes(io, mock_io):
    path = Path("test.txt")
    content = b"test content"

    io.write_file(path, content)

    assert path in io.pending_files
    mock_io.write_bytes.assert_called_once_with(path, content)


def test_write_file_none(io, mock_io):
    path = Path("test.txt")

    io.write_file(path, None)

    assert path not in io.pending_files
    mock_io.untrack_file.assert_called_once_with(path)


def test_save_files_all(io, mock_io):
    paths = {Path("test1.txt"), Path("test2.txt")}
    for path in paths:
        io.write_file(path, "content")

    io.save_files()

    assert len(io.pending_files) == 0
    assert mock_io.save_file.call_count == len(paths)


def test_save_files_subset(io, mock_io):
    path1, path2 = Path("test1.txt"), Path("test2.txt")
    io.write_file(path1, "content1")
    io.write_file(path2, "content2")

    io.save_files({path1})

    assert path2 in io.pending_files
    assert path1 not in io.pending_files
    mock_io.save_file.assert_called_once_with(path1)


def test_check_changes(io, mock_io):
    path = Path("test.txt")
    io.write_file(path, "content")

    io.check_changes()

    assert len(io.pending_files) == 0
    mock_io.check_changes.assert_called_once()


def test_read_bytes(io, mock_io):
    path = Path("test.txt")
    expected = b"content"
    mock_io.read_bytes.return_value = expected

    result = io.read_bytes(path)

    assert result == expected
    mock_io.read_bytes.assert_called_once_with(path)


def test_delete_file(io, mock_io):
    path = Path("test.txt")

    io.delete_file(path)

    mock_io.delete_file.assert_called_once_with(path)
