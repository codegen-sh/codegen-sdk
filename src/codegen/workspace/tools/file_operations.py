"""File operations for manipulating the codebase."""

import os
from typing import Any

from codegen import Codebase
from codegen.sdk.core.directory import Directory


def view_file(codebase: Codebase, filepath: str) -> dict[str, Any]:
    """View the contents and metadata of a file.

    Args:
        codebase: The codebase to operate on
        filepath: Path to the file relative to workspace root

    Returns:
        Dict containing file contents and metadata

    Raises:
        FileNotFoundError: If the file does not exist
    """
    try:
        file = codebase.get_file(filepath)
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


def list_directory(codebase: Codebase, dirpath: str = "./", depth: int = 1) -> dict[str, Any]:
    """List contents of a directory.

    Args:
        codebase: The codebase to operate on
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
        directory = codebase.get_directory(dirpath)
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
                subdir_result = list_directory(codebase, os.path.join(dirpath, item.name), depth=new_depth)
                files.extend(subdir_result["files"])
                subdirs.extend(subdir_result["subdirectories"])

    return {
        "path": str(directory.path),  # Convert PosixPath to string
        "name": directory.name,
        "files": files,
        "subdirectories": subdirs,
    }


def edit_file(codebase: Codebase, filepath: str, content: str) -> dict[str, Any]:
    """Edit a file by replacing its entire content.

    Args:
        codebase: The codebase to operate on
        filepath: Path to the file to edit
        content: New content for the file

    Returns:
        Dict containing updated file state

    Raises:
        FileNotFoundError: If the file does not exist
    """
    try:
        file = codebase.get_file(filepath)
    except ValueError:
        msg = f"File not found: {filepath}"
        raise FileNotFoundError(msg)

    file.edit(content)
    codebase.commit()
    return view_file(codebase, filepath)


def create_file(codebase: Codebase, filepath: str, content: str = "") -> dict[str, Any]:
    """Create a new file.

    Args:
        codebase: The codebase to operate on
        filepath: Path where to create the file
        content: Initial file content

    Returns:
        Dict containing new file state

    Raises:
        FileExistsError: If the file already exists
    """
    if codebase.has_file(filepath):
        msg = f"File already exists: {filepath}"
        raise FileExistsError(msg)
    file = codebase.create_file(filepath, content=content)
    codebase.commit()
    return view_file(codebase, filepath)


def delete_file(codebase: Codebase, filepath: str) -> dict[str, Any]:
    """Delete a file.

    Args:
        codebase: The codebase to operate on
        filepath: Path to the file to delete

    Returns:
        Dict containing deletion status

    Raises:
        FileNotFoundError: If the file does not exist
    """
    try:
        file = codebase.get_file(filepath)
    except ValueError:
        msg = f"File not found: {filepath}"
        raise FileNotFoundError(msg)

    file.remove()
    codebase.commit()
    return {"status": "success", "deleted_file": filepath}


def commit(codebase: Codebase) -> dict[str, Any]:
    """Commit any pending changes to disk.

    Args:
        codebase: The codebase to operate on

    Returns:
        Dict containing commit status
    """
    codebase.commit()
    return {"status": "success", "message": "Changes committed to disk"}
