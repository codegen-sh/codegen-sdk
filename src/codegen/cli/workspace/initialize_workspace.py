import shutil
from pathlib import Path

import rich

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.constants import CODEGEN_DIR, DOCS_DIR, EXAMPLES_DIR, PROMPTS_DIR
from codegen.cli.auth.session import CodegenSession
from codegen.cli.git.repo import get_git_repo
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.workspace.docs_workspace import populate_api_docs
from codegen.cli.workspace.examples_workspace import populate_examples


def initialize_codegen(action: str = "Initializing") -> tuple[Path, Path, Path]:
    """Initialize or update the codegen directory structure and content.

    Args:
        action: The action being performed ("Initializing" or "Updating")

    Returns:
        Tuple of (codegen_folder, docs_folder, examples_folder)

    """
    repo = get_git_repo()
    REPO_PATH = Path(repo.workdir)
    CODEGEN_FOLDER = REPO_PATH / CODEGEN_DIR
    PROMPTS_FOLDER = REPO_PATH / PROMPTS_DIR
    DOCS_FOLDER = REPO_PATH / DOCS_DIR
    EXAMPLES_FOLDER = REPO_PATH / EXAMPLES_DIR

    with create_spinner(f"   {action} folders...") as status:
        # Create folders if they don't exist
        CODEGEN_FOLDER.mkdir(parents=True, exist_ok=True)
        PROMPTS_FOLDER.mkdir(parents=True, exist_ok=True)
        DOCS_FOLDER.mkdir(parents=True, exist_ok=True)
        EXAMPLES_FOLDER.mkdir(parents=True, exist_ok=True)
        if not repo:
            rich.print("No git repository found. Please run this command in a git repository.")
        else:
            status.update(f"   {action} .gitignore...")
            modify_gitignore(CODEGEN_FOLDER)

        # Always fetch and update docs & examples
        status.update("Fetching latest docs & examples...")
        shutil.rmtree(DOCS_FOLDER, ignore_errors=True)
        shutil.rmtree(EXAMPLES_FOLDER, ignore_errors=True)

        session = CodegenSession()
        response = RestAPI(session.token).get_docs()
        populate_api_docs(DOCS_FOLDER, response.docs, status)
        populate_examples(session, EXAMPLES_FOLDER, response.examples, status)

        # Set programming language
        session.config.programming_language = str(response.language)
        session.write_config()

    return CODEGEN_FOLDER, DOCS_FOLDER, EXAMPLES_FOLDER


def add_to_gitignore_if_not_present(gitignore: Path, line: str):
    if not gitignore.exists():
        gitignore.write_text(line)
    elif line not in gitignore.read_text():
        gitignore.write_text(gitignore.read_text() + "\n" + line)


def modify_gitignore(codegen_folder: Path):
    gitignore_path = codegen_folder / ".gitignore"
    add_to_gitignore_if_not_present(gitignore_path, "prompts")
    add_to_gitignore_if_not_present(gitignore_path, "docs")
    add_to_gitignore_if_not_present(gitignore_path, "examples")
