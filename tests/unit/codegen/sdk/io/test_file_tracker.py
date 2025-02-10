from pathlib import Path
from unittest.mock import MagicMock

import pytest

from codegen.sdk.codebase.io.file_io import FileIO
from codegen.sdk.codebase.io.file_tracker import FileTracker


@pytest.fixture
def mock_io():
    return MagicMock(spec=FileIO)


@pytest.fixture
def file_tracker(mock_io):
    return FileTracker(mock_io)


def test_init_default_io():
    tracker = FileTracker()
    assert isinstance(tracker.io, FileIO)
    assert tracker.pending_files == set()


def test_init_custom_io(mock_io):
    tracker = FileTracker(mock_io)
    assert tracker.io == mock_io
    assert tracker.pending_files == set()


def test_write_file_str(file_tracker, mock_io):
    path = Path("test.txt")
    content = "test content"

    file_tracker.write_file(path, content)

    assert path in file_tracker.pending_files
    mock_io.write_text.assert_called_once_with(path, content)


def test_write_file_bytes(file_tracker, mock_io):
    path = Path("test.txt")
    content = b"test content"

    file_tracker.write_file(path, content)

    assert path in file_tracker.pending_files
    mock_io.write_bytes.assert_called_once_with(path, content)


def test_write_file_none(file_tracker, mock_io):
    path = Path("test.txt")

    file_tracker.write_file(path, None)

    assert path not in file_tracker.pending_files
    mock_io.untrack_file.assert_called_once_with(path)


def test_save_files_all(file_tracker, mock_io):
    paths = {Path("test1.txt"), Path("test2.txt")}
    for path in paths:
        file_tracker.write_file(path, "content")

    file_tracker.save_files()

    assert len(file_tracker.pending_files) == 0
    assert mock_io.save_file.call_count == len(paths)


def test_save_files_subset(file_tracker, mock_io):
    path1, path2 = Path("test1.txt"), Path("test2.txt")
    file_tracker.write_file(path1, "content1")
    file_tracker.write_file(path2, "content2")

    file_tracker.save_files({path1})

    assert path2 in file_tracker.pending_files
    assert path1 not in file_tracker.pending_files
    mock_io.save_file.assert_called_once_with(path1)


def test_check_changes(file_tracker, mock_io):
    path = Path("test.txt")
    file_tracker.write_file(path, "content")

    file_tracker.check_changes()

    assert len(file_tracker.pending_files) == 0
    mock_io.check_changes.assert_called_once()


def test_read_bytes(file_tracker, mock_io):
    path = Path("test.txt")
    expected = b"content"
    mock_io.read_bytes.return_value = expected

    result = file_tracker.read_bytes(path)

    assert result == expected
    mock_io.read_bytes.assert_called_once_with(path)


def test_delete_file(file_tracker, mock_io):
    path = Path("test.txt")

    file_tracker.delete_file(path)

    mock_io.delete_file.assert_called_once_with(path)
