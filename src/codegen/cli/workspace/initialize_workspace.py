import shutil
from contextlib import nullcontext
from pathlib import Path

import requests
import rich
import toml
from rich.status import Status

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.constants import CODEGEN_DIR, DOCS_DIR, EXAMPLES_DIR, PROMPTS_DIR
from codegen.cli.auth.session import CodegenSession
from codegen.cli.git.repo import get_git_repo
from codegen.cli.git.url import get_git_organization_and_repo
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.notebooks import create_notebook
from codegen.cli.workspace.docs_workspace import populate_api_docs
from codegen.cli.workspace.examples_workspace import populate_examples
from codegen.cli.workspace.venv_manager import VenvManager


def initialize_codegen(
    status: Status | str = "Initializing",
    session: CodegenSession | None = None,
    fetch_docs: bool = False,
) -> tuple[Path, Path, Path]:
    """Initialize or update the codegen directory structure and content.

    Args:
        status: Either a Status object to update, or a string action being performed ("Initializing" or "Updating")
        session: Optional CodegenSession for fetching docs and examples
        fetch_docs: Whether to fetch docs and examples (requires auth)

    Returns:
        Tuple of (codegen_folder, docs_folder, examples_folder)
    """
    repo = get_git_repo()
    REPO_PATH = Path(repo.workdir)
    CODEGEN_FOLDER = REPO_PATH / CODEGEN_DIR
    PROMPTS_FOLDER = REPO_PATH / PROMPTS_DIR
    DOCS_FOLDER = REPO_PATH / DOCS_DIR
    EXAMPLES_FOLDER = REPO_PATH / EXAMPLES_DIR
    CONFIG_PATH = CODEGEN_FOLDER / "config.toml"
    JUPYTER_DIR = CODEGEN_FOLDER / "jupyter"
    CODEMODS_DIR = CODEGEN_FOLDER / "codemods"
    SYSTEM_PROMPT_PATH = CODEGEN_FOLDER / "codegen-system-prompt.txt"

    # If status is a string, create a new spinner
    context = create_spinner(f"   {status} folders...") if isinstance(status, str) else nullcontext()

    with context as spinner:
        status_obj = spinner if isinstance(status, str) else status

        # Create folders if they don't exist
        CODEGEN_FOLDER.mkdir(parents=True, exist_ok=True)
        PROMPTS_FOLDER.mkdir(parents=True, exist_ok=True)
        JUPYTER_DIR.mkdir(parents=True, exist_ok=True)
        CODEMODS_DIR.mkdir(parents=True, exist_ok=True)

        # Initialize virtual environment
        status_obj.update(f"   {'Creating' if isinstance(status, str) else 'Checking'} virtual environment...")
        venv = VenvManager()
        if not venv.is_initialized():
            venv.create_venv()
            venv.install_packages("codegen")

        # Download system prompt
        try:
            from codegen.cli.api.endpoints import CODEGEN_SYSTEM_PROMPT_URL

            response = requests.get(CODEGEN_SYSTEM_PROMPT_URL)
            response.raise_for_status()
            SYSTEM_PROMPT_PATH.write_text(response.text)
        except Exception as e:
            rich.print(f"[yellow]Warning: Could not download system prompt: {e}[/yellow]")

        if not repo:
            rich.print("No git repository found. Please run this command in a git repository.")
        else:
            status_obj.update(f"   {'Updating' if isinstance(status, Status) else status} .gitignore...")
            modify_gitignore(CODEGEN_FOLDER)

            # Create or update config.toml with basic repo info
            if not session:  # Only create if session doesn't exist (it handles config itself)
                org_name, repo_name = get_git_organization_and_repo(repo)
                config = {}
                if CONFIG_PATH.exists():
                    config = toml.load(CONFIG_PATH)
                config.update(
                    {
                        "organization_name": config.get("organization_name", org_name),
                        "repo_name": config.get("repo_name", repo_name),
                    }
                )
                CONFIG_PATH.write_text(toml.dumps(config))

            # Create notebook template
            create_notebook(JUPYTER_DIR)

        # Only fetch docs and examples if requested and session is provided
        if fetch_docs and session:
            status_obj.update("Fetching latest docs & examples...")
            shutil.rmtree(DOCS_FOLDER, ignore_errors=True)
            shutil.rmtree(EXAMPLES_FOLDER, ignore_errors=True)

            DOCS_FOLDER.mkdir(parents=True, exist_ok=True)
            EXAMPLES_FOLDER.mkdir(parents=True, exist_ok=True)

            response = RestAPI(session.token).get_docs()
            populate_api_docs(DOCS_FOLDER, response.docs, status_obj)
            populate_examples(session, EXAMPLES_FOLDER, response.examples, status_obj)

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
    """Update .gitignore to track only specific Codegen files."""
    gitignore_path = codegen_folder / ".gitignore"

    # Define what should be ignored (everything except config.toml and codemods)
    ignore_patterns = [
        "# Codegen",
        "docs/",
        "examples/",
        "prompts/",
        "jupyter/",
        ".venv/",  # Add venv to gitignore
        "codegen-system-prompt.txt",
        "",
        "# Python cache files",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "",
        "# Keep config.toml and codemods",
        "!config.toml",
        "!codemods/",
        "!codemods/**",
    ]

    # Write or update .gitignore
    if not gitignore_path.exists():
        gitignore_path.write_text("\n".join(ignore_patterns))
    else:
        # Read existing content
        content = gitignore_path.read_text()

        # Check if our section already exists
        if "# Codegen" not in content:
            # Add a newline if the file doesn't end with one
            if content and not content.endswith("\n"):
                content += "\n"
            # Add our patterns
            content += "\n" + "\n".join(ignore_patterns) + "\n"
            gitignore_path.write_text(content)
