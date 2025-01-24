from enum import Enum, auto
from os import PathLike
from pathlib import Path
from typing import NamedTuple, Self

from git import Diff
from watchfiles import Change


class ChangeType(Enum):
    Modified = auto()
    Removed = auto()
    Renamed = auto()
    Added = auto()

    @staticmethod
    def from_watch_change_type(change_type: Change):
        if change_type is Change.added:
            return ChangeType.Added
        elif change_type is Change.deleted:
            return ChangeType.Removed
        elif change_type is Change.modified:
            return ChangeType.Modified

    @staticmethod
    def from_git_change_type(change_type: str | None):
        if change_type == "M":
            return ChangeType.Modified
        if change_type == "D":
            return ChangeType.Removed
        if change_type == "R":
            return ChangeType.Renamed
        if change_type == "A":
            return ChangeType.Added
        raise ValueError(f"Invalid change type: {change_type}")


class DiffLite(NamedTuple):
    """Simple diff for recomputing the graph"""

    change_type: ChangeType
    path: Path
    rename_from: str | None = None
    rename_to: str | None = None

    @classmethod
    def from_watch_change(cls, change: Change, path: PathLike) -> Self:
        return cls(
            change_type=ChangeType.from_watch_change_type(change),
            path=Path(path),
        )

    @classmethod
    def from_git_diff(cls, git_diff: Diff):
        return cls(
            change_type=ChangeType.from_git_change_type(git_diff.change_type),
            path=Path(git_diff.a_path),
            rename_from=git_diff.rename_from,
            rename_to=git_diff.rename_to,
        )

    @classmethod
    def from_reverse_diff(cls, diff_lite: "DiffLite"):
        if diff_lite.change_type == ChangeType.Added:
            change_type = ChangeType.Removed
        elif diff_lite.change_type == ChangeType.Removed:
            change_type = ChangeType.Added
        else:
            change_type = diff_lite.change_type

        if diff_lite.change_type == ChangeType.Renamed:
            return cls(
                change_type=change_type,
                path=diff_lite.path,
                rename_from=diff_lite.rename_to,
                rename_to=diff_lite.rename_from,
            )

        return cls(change_type=change_type, path=diff_lite.path)
