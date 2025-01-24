import builtins
from pathlib import Path

from codegen.cli.utils.function_finder import DecoratedFunction, find_codegen_functions


def _might_have_decorators(file_path: Path) -> bool:
    """Quick check if a file might contain codegen decorators.

    This is a fast pre-filter that checks if '@codegen' appears anywhere in the file.
    Much faster than parsing the AST for files that definitely don't have decorators.
    """
    try:
        # Read in binary mode and check for b'@codegen' to handle any encoding
        with open(file_path, "rb") as f:
            return b"@codegen" in f.read()
    except Exception:
        return False


class CodemodManager:
    """Manages codemod operations in the local filesystem."""

    @staticmethod
    def get_valid_name(name: str) -> str:
        return name.lower().replace(" ", "_").replace("-", "_")

    @classmethod
    def list(cls, start_path: Path | None = None) -> builtins.list[DecoratedFunction]:
        """List all codegen decorated functions in Python files under the given path.

        This is an alias for get_decorated for better readability.
        """
        return cls.get_decorated(start_path)

    @classmethod
    def get(cls, name: str, start_path: Path | None = None) -> DecoratedFunction | None:
        """Get a specific codegen decorated function by name.

        Args:
            name: Name of the function to find (case-insensitive, spaces/hyphens converted to underscores)
            start_path: Directory or file to start searching from. Defaults to current working directory.

        Returns:
            The DecoratedFunction if found, None otherwise

        """
        valid_name = cls.get_valid_name(name)
        functions = cls.get_decorated(start_path)

        for func in functions:
            if cls.get_valid_name(func.name) == valid_name:
                return func
        return None

    @classmethod
    def exists(cls, name: str, start_path: Path | None = None) -> bool:
        """Check if a codegen decorated function with the given name exists.

        Args:
            name: Name of the function to check (case-insensitive, spaces/hyphens converted to underscores)
            start_path: Directory or file to start searching from. Defaults to current working directory.

        Returns:
            True if the function exists, False otherwise

        """
        return cls.get(name, start_path) is not None

    @classmethod
    def get_decorated(cls, start_path: Path | None = None) -> builtins.list[DecoratedFunction]:
        """Find all codegen decorated functions in Python files under the given path.

        Args:
            start_path: Directory or file to start searching from. Defaults to current working directory.

        Returns:
            List of DecoratedFunction objects found in the files

        """
        if start_path is None:
            start_path = Path.cwd()

        # Directories to skip
        SKIP_DIRS = {
            "__pycache__",
            "node_modules",
            ".git",
            ".hg",
            ".svn",
            ".tox",
            ".venv",
            "venv",
            "env",
            "build",
            "dist",
            "site-packages",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".coverage",
            "htmlcov",
            ".codegen",
        }

        all_functions = []
        if start_path.is_file():
            # If it's a file, just check that one
            if start_path.suffix == ".py" and _might_have_decorators(start_path):
                try:
                    functions = find_codegen_functions(start_path)
                    all_functions.extend(functions)
                except Exception as e:
                    pass  # Skip files we can't parse
        else:
            # Walk the directory tree, skipping irrelevant directories
            for path in start_path.rglob("*.py"):
                # Skip if any parent directory is in SKIP_DIRS
                if any(part in SKIP_DIRS for part in path.parts):
                    continue

                if _might_have_decorators(path):
                    try:
                        functions = find_codegen_functions(path)
                        all_functions.extend(functions)
                    except Exception as e:
                        pass  # Skip files we can't parse
        return all_functions
