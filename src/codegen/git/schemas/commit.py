from dataclasses import dataclass
from datetime import datetime

from git import Commit


@dataclass
class GitCommitInfo:
    """Information about a git commit."""

    commit_hash: str
    author: str
    date: datetime
    lines_added: int
    lines_removed: int

    @classmethod
    def from_commit(cls, commit: Commit, filepath: str) -> "GitCommitInfo | None":
        stats = commit.stats.files.get(filepath)
        if not stats:
            return None
        return cls(commit_hash=commit.hexsha, author=commit.author.name or "Unknown", date=commit.committed_datetime, lines_added=stats["insertions"], lines_removed=stats["deletions"])
