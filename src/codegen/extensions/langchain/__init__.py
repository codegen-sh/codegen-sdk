"""Langchain tools for workspace operations."""

from langchain.tools import BaseTool

from codegen import Codebase

from .tools import (
    CommitTool,
    CreateFileTool,
    DeleteFileTool,
    EditFileTool,
    ListDirectoryTool,
    RevealSymbolTool,
    SearchTool,
    ViewFileTool,
)

__all__ = [
    # Tool classes
    "CommitTool",
    "CreateFileTool",
    "DeleteFileTool",
    "EditFileTool",
    "ListDirectoryTool",
    "RevealSymbolTool",
    "SearchTool",
    "ViewFileTool",
    # Helper functions
    "get_workspace_tools",
]


def get_workspace_tools(codebase: Codebase) -> list[BaseTool]:
    """Get all workspace tools initialized with a codebase.

    Args:
        codebase: The codebase to operate on

    Returns:
        List of initialized Langchain tools
    """
    return [
        ViewFileTool(codebase),
        ListDirectoryTool(codebase),
        SearchTool(codebase),
        EditFileTool(codebase),
        CreateFileTool(codebase),
        DeleteFileTool(codebase),
        CommitTool(codebase),
        RevealSymbolTool(codebase),
    ]
