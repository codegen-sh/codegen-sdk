"""Simple text-based search functionality for the codebase.

This performs either a regex pattern match or simple text search across all files in the codebase.
Each matching line will be returned with its line number.
Results are paginated with a default of 10 files per page.
"""

import re
from typing import Any, Optional

from codegen import Codebase


def search(
    codebase: Codebase,
    query: str,
    target_directories: Optional[list[str]] = None,
    file_extensions: Optional[list[str]] = None,
    page: int = 1,
    files_per_page: int = 10,
    use_regex: bool = False,
) -> dict[str, Any]:
    """Search the codebase using text search or regex pattern matching.

    If use_regex is True, performs a regex pattern match on each line.
    Otherwise, performs a case-insensitive text search.
    Returns matching lines with their line numbers, grouped by file.
    Results are paginated by files, with a default of 10 files per page.

    Args:
        codebase: The codebase to operate on
        query: The text to search for or regex pattern to match
        target_directories: Optional list of directories to search in
        file_extensions: Optional list of file extensions to search (e.g. ['.py', '.ts'])
        page: Page number to return (1-based, default: 1)
        files_per_page: Number of files to return per page (default: 10)
        use_regex: Whether to treat query as a regex pattern (default: False)

    Returns:
        Dict containing search results with matches and their sources, grouped by file:
        {
            "query": str,
            "page": int,
            "total_pages": int,
            "total_files": int,
            "files_per_page": int,
            "results": [
                {
                    "filepath": str,
                    "matches": [
                        {
                            "line_number": int,  # 1-based line number
                            "line": str,         # The full line containing the match
                            "match": str,        # The specific text that matched
                        }
                    ]
                }
            ]
        }

    Raises:
        re.error: If use_regex is True and the regex pattern is invalid
    """
    # Validate pagination parameters
    if page < 1:
        page = 1
    if files_per_page < 1:
        files_per_page = 10

    # Prepare the search pattern
    if use_regex:
        try:
            pattern = re.compile(query)
        except re.error as e:
            msg = f"Invalid regex pattern: {e!s}"
            raise re.error(msg) from e
    else:
        # For non-regex searches, escape special characters and make case-insensitive
        pattern = re.compile(re.escape(query), re.IGNORECASE)

    all_results = []
    for file in codebase.files:
        # Skip if file doesn't match target directories
        if target_directories and not any(file.filepath.startswith(d) for d in target_directories):
            continue

        # Skip if file extension doesn't match
        if file_extensions and not any(file.filepath.endswith(ext) for ext in file_extensions):
            continue

        file_matches = []
        # Split content into lines and store with line numbers (1-based)
        lines = enumerate(file.content.splitlines(), 1)

        # Search each line for the pattern
        for line_number, line in lines:
            match = pattern.search(line)
            if match:
                file_matches.append(
                    {
                        "line_number": line_number,
                        "line": line.strip(),
                        "match": match.group(0),  # The full matched text
                    }
                )

        if file_matches:
            all_results.append({"filepath": file.filepath, "matches": sorted(file_matches, key=lambda x: x["line_number"])})

    # Sort all results by filepath
    all_results.sort(key=lambda x: x["filepath"])

    # Calculate pagination
    total_files = len(all_results)
    total_pages = (total_files + files_per_page - 1) // files_per_page
    start_idx = (page - 1) * files_per_page
    end_idx = start_idx + files_per_page

    # Get the current page of results
    paginated_results = all_results[start_idx:end_idx]

    return {
        "query": query,
        "page": page,
        "total_pages": total_pages,
        "total_files": total_files,
        "files_per_page": files_per_page,
        "results": paginated_results,
    }
