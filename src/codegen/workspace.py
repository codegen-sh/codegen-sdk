import os
from typing import Optional

from codegen import Codebase
from codegen.sdk.core.directory import Directory


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
        try:
            file = self.codebase.get_file(filepath)
        except ValueError:
            msg = f"File not found: {filepath}"
            raise FileNotFoundError(msg)

        if not file:
            msg = f"File not found: {filepath}"
            raise FileNotFoundError(msg)

        return {
            "filepath": file.filepath,
            "content": file.content,
            "extension": file.extension,
            "name": file.name,
            "functions": [f.name for f in file.functions],
            "classes": [c.name for c in file.classes],
            "imports": [i.source for i in file.imports],
        }

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
        try:
            directory = self.codebase.get_directory(dirpath)
        except ValueError:
            msg = f"Directory not found: {dirpath}"
            raise NotADirectoryError(msg)

        if not directory:
            msg = f"Directory not found: {dirpath}"
            raise NotADirectoryError(msg)

        # Get immediate files
        files = []
        subdirs = []

        for item in directory.items.values():
            if isinstance(item, Directory):
                subdirs.append(item.name)
            else:
                # Get full filename with extension from filepath
                files.append(os.path.basename(item.filepath))

        # If depth > 1 or unlimited (-1), recursively get subdirectories
        if depth != 1:
            new_depth = depth - 1 if depth > 1 else -1
            for item in directory.items.values():
                if isinstance(item, Directory):
                    subdir_result = self.list_directory(os.path.join(dirpath, item.name), depth=new_depth)
                    files.extend(subdir_result["files"])
                    subdirs.extend(subdir_result["subdirectories"])

        return {"path": directory.path, "name": directory.name, "files": files, "subdirectories": subdirs}

    def search(self, query: str, target_directories: Optional[list[str]] = None) -> dict:
        """Search the codebase using semantic search.

        Args:
            query: The search query
            target_directories: Optional list of directories to search in

        Returns:
            Dict containing search results
        """
        results = []
        for file in self.codebase.files:
            if target_directories and not any(file.filepath.startswith(d) for d in target_directories):
                continue

            matches = file.search(query)
            if matches:
                results.append({"filepath": file.filepath, "matches": [m.source for m in matches]})

        return {"query": query, "results": results}

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
        file = self.codebase.get_file(filepath)
        if not file:
            msg = f"File not found: {filepath}"
            raise FileNotFoundError(msg)

        file.edit(content)
        self.codebase.commit()
        return self.view_file(filepath)

    def create_file(self, filepath: str, content: str = "") -> dict:
        """Create a new file.

        Args:
            filepath: Path where to create the file
            content: Initial file content

        Returns:
            Dict containing new file state
        """
        if self.codebase.has_file(filepath):
            msg = f"File already exists: {filepath}"
            raise FileExistsError(msg)
        file = self.codebase.create_file(filepath, content=content)
        self.codebase.commit()
        return self.view_file(filepath)

    def delete_file(self, filepath: str) -> dict:
        """Delete a file.

        Args:
            filepath: Path to the file to delete

        Returns:
            Dict containing deletion status
        """
        try:
            file = self.codebase.get_file(filepath)
        except ValueError:
            msg = f"File not found: {filepath}"
            raise FileNotFoundError(msg)

        file.remove()
        self.codebase.commit()
        return {"status": "success", "deleted_file": filepath}

    def commit(self) -> dict:
        """Commit any pending changes to disk.

        Returns:
            Dict containing commit status
        """
        self.codebase.commit()
        return {"status": "success", "message": "Changes committed to disk"}
