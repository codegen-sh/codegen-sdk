from pathlib import Path


def get_success_message(codegen_dir: Path, docs_dir: Path, examples_dir: Path) -> str:
    """Get the success message to display after initialization."""
    return """📁 .codegen configuration folder created:
   [dim]config.toml[/dim]                Project configuration
   [dim]codemods/[/dim]                  Your codemod implementations
   [dim].venv/[/dim]                     Python virtual environment (gitignored)
   [dim]codegen-system-prompt.txt[/dim]  AI system prompt (gitignored)"""
