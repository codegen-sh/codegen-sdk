"""File operations for manipulating the codebase."""

import os
from typing import Any, Literal

from codegen import Codebase
from codegen.sdk.core.directory import Directory


def view_file(codebase: Codebase, filepath: str) -> dict[str, Any]:
    """View the contents and metadata of a file.

    Args:
        codebase: The codebase to operate on
        filepath: Path to the file relative to workspace root

    Returns:
        Dict containing file contents and metadata, or error information if file not found
    """
    try:
        file = codebase.get_file(filepath)
    except ValueError:
        return {"error": f"File not found: {filepath}"}

    if not file:
        return {"error": f"File not found: {filepath}"}

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

    TODO(CG-10729): add support for directories that only including non-SourceFiles (code files). At the moment,
     only files and directories that have SourceFile objects are included.

    Args:
        codebase: The codebase to operate on
        dirpath: Path to directory relative to workspace root
        depth: How deep to traverse the directory tree. Default is 1 (immediate children only).
               Use -1 for unlimited depth.

    Returns:
        Dict containing directory contents and metadata, or error information if directory not found
    """
    try:
        directory = codebase.get_directory(dirpath)
    except ValueError:
        return {"error": f"Directory not found: {dirpath}"}

    if not directory:
        return {"error": f"Directory not found: {dirpath}"}

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
                if "error" not in subdir_result:
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
        Dict containing updated file state, or error information if file not found
    """
    try:
        file = codebase.get_file(filepath)
    except ValueError:
        return {"error": f"File not found: {filepath}"}

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
        Dict containing new file state, or error information if file already exists
    """
    if codebase.has_file(filepath):
        return {"error": f"File already exists: {filepath}"}
    file = codebase.create_file(filepath, content=content)
    codebase.commit()
    return view_file(codebase, filepath)


def delete_file(codebase: Codebase, filepath: str) -> dict[str, Any]:
    """Delete a file.

    Args:
        codebase: The codebase to operate on
        filepath: Path to the file to delete

    Returns:
        Dict containing deletion status, or error information if file not found
    """
    try:
        file = codebase.get_file(filepath)
    except ValueError:
        return {"error": f"File not found: {filepath}"}

    file.remove()
    codebase.commit()
    return {"status": "success", "deleted_file": filepath}


def rename_file(codebase: Codebase, filepath: str, new_filepath: str) -> dict[str, Any]:
    """Rename a file and update all imports to point to the new location.

    Args:
        codebase: The codebase to operate on
        filepath: Current path of the file relative to workspace root
        new_filepath: New path for the file relative to workspace root

    Returns:
        Dict containing rename status and new file info, or error information if file not found
    """
    try:
        file = codebase.get_file(filepath)
    except ValueError:
        return {"error": f"File not found: {filepath}"}

    if codebase.has_file(new_filepath):
        return {"error": f"Destination file already exists: {new_filepath}"}

    try:
        file.update_filepath(new_filepath)
        codebase.commit()
        return {"status": "success", "old_filepath": filepath, "new_filepath": new_filepath, "file_info": view_file(codebase, new_filepath)}
    except Exception as e:
        return {"error": f"Failed to rename file: {e!s}"}


def move_symbol(
    codebase: Codebase,
    source_file: str,
    symbol_name: str,
    target_file: str,
    strategy: Literal["update_all_imports", "add_back_edge"] = "update_all_imports",
    include_dependencies: bool = True,
) -> dict[str, Any]:
    """Move a symbol from one file to another.

    Args:
        codebase: The codebase to operate on
        source_file: Path to the file containing the symbol
        symbol_name: Name of the symbol to move
        target_file: Path to the destination file
        strategy: Strategy for handling imports:
                 - "update_all_imports": Updates all import statements across the codebase (default)
                 - "add_back_edge": Adds import and re-export in the original file
        include_dependencies: Whether to move dependencies along with the symbol

    Returns:
        Dict containing move status and updated file info, or error information if operation fails
    """
    try:
        source = codebase.get_file(source_file)
    except ValueError:
        return {"error": f"Source file not found: {source_file}"}

    try:
        target = codebase.get_file(target_file)
    except ValueError:
        return {"error": f"Target file not found: {target_file}"}

    symbol = source.get_symbol(symbol_name)
    if not symbol:
        return {"error": f"Symbol '{symbol_name}' not found in {source_file}"}

    try:
        symbol.move_to_file(target, include_dependencies=include_dependencies, strategy=strategy)
        codebase.commit()
        return {
            "status": "success",
            "symbol": symbol_name,
            "source_file": source_file,
            "target_file": target_file,
            "source_file_info": view_file(codebase, source_file),
            "target_file_info": view_file(codebase, target_file),
        }
    except Exception as e:
        return {"error": f"Failed to move symbol: {e!s}"}


def commit(codebase: Codebase) -> dict[str, Any]:
    """Commit any pending changes to disk.

    Args:
        codebase: The codebase to operate on

    Returns:
        Dict containing commit status
    """
    codebase.commit()
    return {"status": "success", "message": "Changes committed to disk"}


def make_pr(codebase: Codebase, title: str, body: str, branch: str | None = None) -> dict[str, Any]:
    """Creates a pull request or returns a URL to create one.

    Args:
        codebase: The codebase to operate on
        title: The title for the pull request
        body: The description/body for the pull request
        branch: Optional branch name to create PR from. If provided, will checkout/create branch and push to it.

    Returns:
        Dict containing either:
        - On success: {"status": "success", "url": "<pr_url>", "number": pr_number}
        - On manual URL: {"status": "manual", "url": "<url_to_create_pr>"}
        - On error: {"error": "<error_message>"}
    """
    return codebase.make_pr(title=title, body=body, branch=branch)
