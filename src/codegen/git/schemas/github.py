from enum import StrEnum, auto
from typing import Self


class GithubScope(StrEnum):
    READ = "read"
    WRITE = "write"


class GithubType(StrEnum):
    Github = auto()  # aka public Github
    GithubEnterprise = auto()

    def __str__(self) -> str:
        return self.name

    @property
    def hostname(self) -> str:
        if self == GithubType.Github:
            return "github.com"
        elif self == GithubType.GithubEnterprise:
            return "github.codegen.app"
        else:
            msg = f"Invalid GithubType: {self}"
            raise ValueError(msg)

    @property
    def base_url(self) -> str:
        return f"https://{self.hostname}"

    @classmethod
    def from_url(cls, url: str) -> Self:
        for github_type in cls:
            if github_type.hostname in url:
                return github_type
        msg = f"Could not find GithubType from url: {url}"
        raise ValueError(msg)

    @classmethod
    def from_string(cls, value: str) -> Self:
        try:
            return cls[value]  # This will match the exact name
        except KeyError:
            msg = f"'{value}' is not a valid GithubType. Valid values are: {[e.name for e in cls]}"
            raise ValueError(msg)
