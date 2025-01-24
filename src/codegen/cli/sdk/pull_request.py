from unidiff import PatchSet

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.session import CodegenSession


class CodegenPullRequest:
    """Interface to PullRequests by humans"""

    url: str
    number: int
    title: str
    github_pr_number: int
    codegen_pr_id: int
    patch_set: PatchSet | None = None

    def __init__(self, url: str, number: int, title: str, github_pr_number: int, codegen_pr_id: int, patch_set: PatchSet | None = None):
        self.url = url
        self.number = number
        self.title = title
        self.github_pr_number = github_pr_number
        self.codegen_pr_id = codegen_pr_id
        self.patch_set = patch_set

    @classmethod
    def lookup(cls, number: int) -> "CodegenPullRequest":
        """Look up a pull request by its GitHub PR number.

        Args:
            number: GitHub PR number to look up

        Returns:
            A CodegenPullRequest instance representing the PR

        """
        session = CodegenSession()
        api_client = RestAPI(session.token)
        response = api_client.lookup_pr(repo_full_name=session.repo_name, github_pr_number=number)
        pr = response.pr

        return cls(
            url=pr.url,
            number=number,
            title=pr.title,
            github_pr_number=pr.github_pr_number,
            codegen_pr_id=pr.codegen_pr_id,
            patch_set=None,  # Can be loaded on demand if needed
        )

    def __str__(self):
        return f"CodegenPullRequest(url={self.url}, number={self.number}, title={self.title}, github_pr_number={self.github_pr_number}, codegen_pr_id={self.codegen_pr_id})"
