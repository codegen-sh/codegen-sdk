"""Headless workspace for code manipulation."""

from typing import Any, Optional

from codegen import Codebase

from .tools import (
    commit as commit_tool,
)
from .tools import (
    create_file as create_file_tool,
)
from .tools import (
    delete_file as delete_file_tool,
)
from .tools import (
    edit_file as edit_file_tool,
)
from .tools import (
    list_directory as list_directory_tool,
)
from .tools import (
    reveal_symbol as reveal_symbol_tool,
)
from .tools import (
    search as search_tool,
)
from .tools import (
    view_file as view_file_tool,
)


class Workspace:
    """A headless workspace that provides standard file/directory operations."""

    codebase: Codebase

    def __init__(self, codebase: Codebase):
        """Initialize the workspace with a Codebase instance.

        Args:
            codebase: The Codebase instance to wrap
        """
        self.codebase = codebase

    def view_file(self, filepath: str) -> dict:
        """View the contents and metadata of a file.

        Args:
            filepath: Path to the file relative to workspace root

        Returns:
            Dict containing file contents and metadata

        Raises:
            FileNotFoundError: If the file does not exist
        """
        return view_file_tool(self.codebase, filepath)

    def list_directory(self, dirpath: str = "./", depth: int = 1) -> dict:
        """List contents of a directory.

        Args:
            dirpath: Path to directory relative to workspace root
            depth: How deep to traverse the directory tree. Default is 1 (immediate children only).
                  Use -1 for unlimited depth.

        Returns:
            Dict containing directory contents and metadata:
                - path: Full path of the directory
                - name: Name of the directory
                - files: List of file names (with extensions) in the directory
                - subdirectories: List of subdirectory names (not full paths)

        Raises:
            NotADirectoryError: If the directory does not exist
        """
        return list_directory_tool(self.codebase, dirpath, depth)

    def search(self, query: str, target_directories: Optional[list[str]] = None) -> dict:
        """Search the codebase using semantic search.

        Args:
            query: The search query
            target_directories: Optional list of directories to search in

        Returns:
            Dict containing search results
        """
        return search_tool(self.codebase, query, target_directories)

    def edit_file(self, filepath: str, content: str) -> dict:
        """Edit a file by replacing its entire content.

        Args:
            filepath: Path to the file to edit
            content: New content for the file

        Returns:
            Dict containing updated file state

        Raises:
            FileNotFoundError: If the file does not exist
        """
        return edit_file_tool(self.codebase, filepath, content)

    def create_file(self, filepath: str, content: str = "") -> dict:
        """Create a new file.

        Args:
            filepath: Path where to create the file
            content: Initial file content

        Returns:
            Dict containing new file state

        Raises:
            FileExistsError: If the file already exists
        """
        return create_file_tool(self.codebase, filepath, content)

    def delete_file(self, filepath: str) -> dict:
        """Delete a file.

        Args:
            filepath: Path to the file to delete

        Returns:
            Dict containing deletion status

        Raises:
            FileNotFoundError: If the file does not exist
        """
        return delete_file_tool(self.codebase, filepath)

    def commit(self) -> dict:
        """Commit any pending changes to disk.

        Returns:
            Dict containing commit status
        """
        return commit_tool(self.codebase)

    def reveal_symbol(
        self,
        symbol_name: str,
        degree: int = 1,
        max_tokens: Optional[int] = None,
        collect_dependencies: bool = True,
        collect_usages: bool = True,
    ) -> dict[str, Any]:
        """Reveal the dependencies and usages of a symbol up to N degrees.

        Args:
            symbol_name: Name of the symbol to analyze
            degree: How many degrees of separation to traverse (default: 1)
            max_tokens: Optional maximum number of tokens for all source code combined.
                       If provided, will intelligently truncate source code to fit within the limit.
            collect_dependencies: Whether to collect dependencies (default: True)
            collect_usages: Whether to collect usages (default: True)

        Returns:
            Dict containing:
                - dependencies: List of symbols this symbol depends on (if collect_dependencies=True)
                - usages: List of symbols that use this symbol (if collect_usages=True)
                - truncated: Whether the results were truncated due to max_tokens
                - error: Optional error message if the symbol was not found
        """
        # Find the symbol
        found_symbol = None
        for file in self.codebase.files:
            for symbol in file.symbols:
                if symbol.name == symbol_name:
                    found_symbol = symbol
                    break
            if found_symbol:
                break

        return reveal_symbol_tool(
            found_symbol,
            degree,
            max_tokens,
            collect_dependencies=collect_dependencies,
            collect_usages=collect_usages,
        )
