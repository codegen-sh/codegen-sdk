from pydantic import BaseModel

from codegen.shared.decorators.docs import apidoc


@apidoc
class PROptions(BaseModel):
    """Options for generating a PR."""

    title: str | None = None
    body: str | None = None
    labels: list[str] | None = None  # TODO: not used until we add labels to GithubPullRequestModel
    force_push_head_branch: bool | None = None
