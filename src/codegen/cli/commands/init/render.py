from pathlib import Path


def get_success_message(codegen_dir: Path, docs_dir: Path, examples_dir: Path) -> str:
    """Get the success message to display after initialization."""
    return """📁 Folders Created:
   [dim] Location:[/dim]  .codegen
   [dim] Docs:[/dim]      .codegen/docs
   [dim] Examples:[/dim]  .codegen/examples"""
