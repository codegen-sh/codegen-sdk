import giturlparse
from pygit2.repository import Repository


def get_git_organization_and_repo(repo: Repository) -> tuple[str, str]:
    for remote in repo.remotes:
        if remote.name == "origin":
            parsed = giturlparse.parse(remote.url)
            return parsed.owner, parsed.name
    raise ValueError("No git remote found")
