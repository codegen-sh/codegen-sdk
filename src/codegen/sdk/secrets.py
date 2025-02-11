from dataclasses import dataclass


@dataclass
class Secrets:
    openai_key: str | None = None
    github_api_key: str | None = None
