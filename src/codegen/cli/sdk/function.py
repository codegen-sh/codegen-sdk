from dataclasses import dataclass
from pathlib import Path

from codegen.cli.api.client import RestAPI
from codegen.cli.api.schemas import CodemodRunType, RunCodemodOutput
from codegen.cli.auth.session import CodegenSession
from codegen.cli.utils.codemods import Codemod
from codegen.cli.utils.schema import CodemodConfig


@dataclass
class PullRequest:
    """A pull request created by a codemod."""

    url: str
    number: int
    title: str


@dataclass
class Function:
    """A deployed codegen function that can be run."""

    name: str
    codemod_id: int
    version_id: int
    _api_client: RestAPI | None = None

    @classmethod
    def lookup(cls, name: str) -> "Function":
        """Look up a deployed function by name."""
        session = CodegenSession()
        api_client = RestAPI(session.token)
        response = api_client.lookup(name)

        return cls(name=name, codemod_id=response.codemod_id, version_id=response.version_id, _api_client=api_client)

    def run(self, pr: bool = False, **kwargs) -> RunCodemodOutput:
        """Run the function with the given arguments.

        Args:
            pr: Whether to create a pull request with the changes
            **kwargs: Parameters to pass to the function

        Returns:
            The raw output from the run API, containing fields like:
            - success: bool
            - web_link: Optional[str]
            - logs: Optional[str]
            - observation: Optional[str] (the diff)
            - error: Optional[str]

        """
        if self._api_client is None:
            session = CodegenSession()
            self._api_client = RestAPI(session.token)

        # Create a temporary codemod object to use with the API
        config = CodemodConfig(
            name=self.name,
            codemod_id=self.codemod_id,
            description=None,
            created_at="",  # Not needed for running
            created_by="",  # Not needed for running
        )

        codemod = Codemod(
            name=self.name,
            config=config,
            path=Path("."),  # Not used since we're not reading from disk
        )

        # Don't include source code since we want to use the deployed version
        return self._api_client.run(codemod, include_source=False, run_type=CodemodRunType.PR if pr else CodemodRunType.DIFF, template_context=kwargs)
