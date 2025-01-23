import logging
import os

from codegen_git.repo_operator.local_repo_operator import LocalRepoOperator
from graph_sitter.codebase.config import DefaultConfig, ProjectConfig
from graph_sitter.core.codebase import Codebase
from graph_sitter.utils import determine_project_language

logger = logging.getLogger(__name__)

DEFAULT_CODEGEN_DIR = "/tmp/codegen"


def fetch_codebase(repo_name: str, *, tmp_dir: str | None = None, shallow: bool = True, commit_hash: str | None = None) -> Codebase:
    """Fetches a codebase from GitHub and returns a Codebase instance.

    Args:
        repo_name (str): The name of the repository in format "owner/repo"
        tmp_dir (Optional[str]): The directory to clone the repo into. Defaults to /tmp/codegen
        shallow (bool): Whether to do a shallow clone. Defaults to True
        commit_hash (Optional[str]): The specific commit hash to clone. Defaults to HEAD
    Returns:
        Codebase: A Codebase instance initialized with the cloned repository
    Example:
        ```python
        import graph_sitter
        import logging
        # Enable logging to see progress
        logging.basicConfig(level=logging.INFO)
        # Clone a repository to default location (/tmp/codegen)
        codebase = graph_sitter.fetch_codebase('facebook/react')
        # Or specify a custom directory
        codebase = graph_sitter.fetch_codebase('facebook/react', tmp_dir='~/my_repos')
        # Or clone a specific commit
        codebase = graph_sitter.fetch_codebase('facebook/react', commit_hash='abc123')
        ```
    """
    logger.info(f"Fetching codebase for {repo_name}")

    # Parse repo name
    if "/" not in repo_name:
        raise ValueError("repo_name must be in format 'owner/repo'")
    owner, repo = repo_name.split("/")

    # Setup temp directory
    if tmp_dir is None:
        tmp_dir = DEFAULT_CODEGEN_DIR
    os.makedirs(tmp_dir, exist_ok=True)
    logger.info(f"Using directory: {tmp_dir}")

    # Setup repo path and URL
    repo_path = os.path.join(tmp_dir, repo)
    repo_url = f"https://github.com/{repo_name}.git"
    logger.info(f"Will clone {repo_url} to {repo_path}")

    try:
        # Use LocalRepoOperator to fetch the repository
        logger.info("Cloning repository...")
        repo_operator = LocalRepoOperator.create_from_commit(
            repo_path=repo_path,
            default_branch="main",  # We'll get the actual default branch after clone
            commit=commit_hash or "HEAD",
            url=repo_url,
        )
        logger.info("Clone completed successfully")

        # Initialize and return codebase with proper context
        logger.info("Initializing Codebase...")
        project = ProjectConfig(repo_operator=repo_operator, programming_language=determine_project_language(repo_path))
        codebase = Codebase(projects=[project], config=DefaultConfig)
        logger.info("Codebase initialization complete")
        return codebase
    except Exception as e:
        logger.error(f"Failed to initialize codebase: {e}")
        raise
