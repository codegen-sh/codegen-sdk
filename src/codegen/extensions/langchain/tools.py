"""Langchain tools for workspace operations."""

import json
import uuid
from typing import ClassVar, Literal, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools.base import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from codegen import Codebase
from codegen.extensions.tools.file_operations import (
    commit,
    create_file,
    delete_file,
    edit_file,
    list_directory,
    move_symbol,
    rename_file,
    view_file,
)
from codegen.extensions.tools.reveal_symbol import reveal_symbol
from codegen.extensions.tools.search import search
from codegen.extensions.tools.semantic_edit import semantic_edit
from codegen.extensions.tools.semantic_search import semantic_search

from .tool_prompts import _FILE_EDIT_DESCRIPTION, _HUMAN_PROMPT_DRAFT_EDITOR, _SYSTEM_PROMPT_DRAFT_EDITOR


class ViewFileInput(BaseModel):
    """Input for viewing a file."""

    filepath: str = Field(..., description="Path to the file relative to workspace root")


class ViewFileTool(BaseTool):
    """Tool for viewing file contents and metadata."""

    name: ClassVar[str] = "view_file"
    description: ClassVar[str] = "View the contents and metadata of a file in the codebase"
    args_schema: ClassVar[type[BaseModel]] = ViewFileInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, filepath: str) -> str:
        result = view_file(self.codebase, filepath)
        return json.dumps(result, indent=2)


class ListDirectoryInput(BaseModel):
    """Input for listing directory contents."""

    dirpath: str = Field(default="./", description="Path to directory relative to workspace root")
    depth: int = Field(default=1, description="How deep to traverse. Use -1 for unlimited depth.")


class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents."""

    name: ClassVar[str] = "list_directory"
    description: ClassVar[str] = "List contents of a directory in the codebase"
    args_schema: ClassVar[type[BaseModel]] = ListDirectoryInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, dirpath: str = "./", depth: int = 1) -> str:
        result = list_directory(self.codebase, dirpath, depth)
        return json.dumps(result, indent=2)


class SearchInput(BaseModel):
    """Input for searching the codebase."""

    query: str = Field(..., description="The search query, passed into python's re.match()")
    target_directories: Optional[list[str]] = Field(default=None, description="Optional list of directories to search in")


class SearchTool(BaseTool):
    """Tool for searching the codebase."""

    name: ClassVar[str] = "search"
    description: ClassVar[str] = "Search the codebase using text search"
    args_schema: ClassVar[type[BaseModel]] = SearchInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, query: str, target_directories: Optional[list[str]] = None) -> str:
        result = search(self.codebase, query, target_directories)
        return json.dumps(result, indent=2)


class EditFileInput(BaseModel):
    """Input for editing a file."""

    filepath: str = Field(..., description="Path to the file to edit")
    content: str = Field(..., description="New content for the file")


class EditFileTool(BaseTool):
    """Tool for editing files."""

    name: ClassVar[str] = "edit_file"
    description: ClassVar[str] = "Edit a file by replacing its entire content. This tool should only be used for replacing entire file contents."
    args_schema: ClassVar[type[BaseModel]] = EditFileInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, filepath: str, content: str) -> str:
        result = edit_file(self.codebase, filepath, content)
        return json.dumps(result, indent=2)


class CreateFileInput(BaseModel):
    """Input for creating a file."""

    filepath: str = Field(..., description="Path where to create the file")
    content: str = Field(default="", description="Initial file content")


class CreateFileTool(BaseTool):
    """Tool for creating files."""

    name: ClassVar[str] = "create_file"
    description: ClassVar[str] = "Create a new file in the codebase"
    args_schema: ClassVar[type[BaseModel]] = CreateFileInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, filepath: str, content: str = "") -> str:
        result = create_file(self.codebase, filepath, content)
        return json.dumps(result, indent=2)


class DeleteFileInput(BaseModel):
    """Input for deleting a file."""

    filepath: str = Field(..., description="Path to the file to delete")


class DeleteFileTool(BaseTool):
    """Tool for deleting files."""

    name: ClassVar[str] = "delete_file"
    description: ClassVar[str] = "Delete a file from the codebase"
    args_schema: ClassVar[type[BaseModel]] = DeleteFileInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, filepath: str) -> str:
        result = delete_file(self.codebase, filepath)
        return json.dumps(result, indent=2)


class CommitTool(BaseTool):
    """Tool for committing changes."""

    name: ClassVar[str] = "commit"
    description: ClassVar[str] = "Commit any pending changes to disk"
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self) -> str:
        result = commit(self.codebase)
        return json.dumps(result, indent=2)


class RevealSymbolInput(BaseModel):
    """Input for revealing symbol relationships."""

    symbol_name: str = Field(..., description="Name of the symbol to analyze")
    degree: int = Field(default=1, description="How many degrees of separation to traverse")
    max_tokens: Optional[int] = Field(default=None, description="Optional maximum number of tokens for all source code combined")
    collect_dependencies: bool = Field(default=True, description="Whether to collect dependencies")
    collect_usages: bool = Field(default=True, description="Whether to collect usages")


class RevealSymbolTool(BaseTool):
    """Tool for revealing symbol relationships."""

    name: ClassVar[str] = "reveal_symbol"
    description: ClassVar[str] = "Reveal the dependencies and usages of a symbol up to N degrees"
    args_schema: ClassVar[type[BaseModel]] = RevealSymbolInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(
        self,
        symbol_name: str,
        degree: int = 1,
        max_tokens: Optional[int] = None,
        collect_dependencies: bool = True,
        collect_usages: bool = True,
    ) -> str:
        # Find the symbol first
        found_symbol = self.codebase.get_symbol(symbol_name)
        result = reveal_symbol(
            found_symbol,
            degree,
            max_tokens,
            collect_dependencies=collect_dependencies,
            collect_usages=collect_usages,
        )
        return json.dumps(result, indent=2)


_SEMANTIC_EDIT_BRIEF = """Tool for semantic editing of files.
* Allows editing files by providing a draft of the new content
* For large files, specify line ranges to edit
* Will intelligently handle unchanged sections of code. Also supports appending to the end of a file."""


class SemanticEditInput(BaseModel):
    """Input for semantic editing."""

    filepath: str = Field(..., description="Path of the file relative to workspace root")
    edit_content: str = Field(..., description=_FILE_EDIT_DESCRIPTION)
    start: int = Field(default=1, description="Starting line number (1-indexed, inclusive). Default is 1.")
    end: int = Field(default=-1, description="Ending line number (1-indexed, inclusive). Default is -1 (end of file).")


class SemanticEditTool(BaseTool):
    """Tool for semantic editing of files."""

    name: ClassVar[str] = "semantic_edit"
    description: ClassVar[str] = _SEMANTIC_EDIT_BRIEF  # Short description
    args_schema: ClassVar[type[BaseModel]] = SemanticEditInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, filepath: str, edit_content: str, start: int = 1, end: int = -1) -> str:
        # Create the the draft editor mini llm
        system_message = _SYSTEM_PROMPT_DRAFT_EDITOR
        human_message = _HUMAN_PROMPT_DRAFT_EDITOR

        prompt = ChatPromptTemplate.from_messages([system_message, human_message])
        # Call the draft editor
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=10000,
        )

        chain = prompt | llm

        result = semantic_edit(self.codebase, filepath, edit_content, llm=chain, start=start, end=end)
        return json.dumps(result, indent=2)


class RenameFileInput(BaseModel):
    """Input for renaming a file."""

    filepath: str = Field(..., description="Current path of the file relative to workspace root")
    new_filepath: str = Field(..., description="New path for the file relative to workspace root")


class RenameFileTool(BaseTool):
    """Tool for renaming files and updating imports."""

    name: ClassVar[str] = "rename_file"
    description: ClassVar[str] = "Rename a file and update all imports to point to the new location"
    args_schema: ClassVar[type[BaseModel]] = RenameFileInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, filepath: str, new_filepath: str) -> str:
        result = rename_file(self.codebase, filepath, new_filepath)
        return json.dumps(result, indent=2)


class MoveSymbolInput(BaseModel):
    """Input for moving a symbol between files."""

    source_file: str = Field(..., description="Path to the file containing the symbol")
    symbol_name: str = Field(..., description="Name of the symbol to move")
    target_file: str = Field(..., description="Path to the destination file")
    strategy: Literal["update_all_imports", "add_back_edge"] = Field(default="update_all_imports", description="Strategy for handling imports: 'update_all_imports' (default) or 'add_back_edge'")
    include_dependencies: bool = Field(default=True, description="Whether to move dependencies along with the symbol")


class MoveSymbolTool(BaseTool):
    """Tool for moving symbols between files."""

    name: ClassVar[str] = "move_symbol"
    description: ClassVar[str] = "Move a symbol from one file to another, with configurable import handling"
    args_schema: ClassVar[type[BaseModel]] = MoveSymbolInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(
        self,
        source_file: str,
        symbol_name: str,
        target_file: str,
        strategy: Literal["update_all_imports", "add_back_edge"] = "update_all_imports",
        include_dependencies: bool = True,
    ) -> str:
        result = move_symbol(
            self.codebase,
            source_file,
            symbol_name,
            target_file,
            strategy=strategy,
            include_dependencies=include_dependencies,
        )
        return json.dumps(result, indent=2)


class SemanticSearchInput(BaseModel):
    """Input for Semantic search of a codebase"""

    query: str = Field(..., description="The natural language search query")
    k: int = Field(default=5, description="Number of results to return")
    preview_length: int = Field(default=200, description="Length of content preview in characters")


class SemanticSearchTool(BaseTool):
    """Tool for semantic code search."""

    name: ClassVar[str] = "semantic_search"
    description: ClassVar[str] = "Search the codebase using natural language queries and semantic similarity"
    args_schema: ClassVar[type[BaseModel]] = SemanticSearchInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, query: str, k: int = 5, preview_length: int = 200) -> str:
        result = semantic_search(self.codebase, query, k=k, preview_length=preview_length)
        return json.dumps(result, indent=2)


class CreatePRInput(BaseModel):
    """Input for creating a PR"""

    title: str = Field(..., description="The title of the PR")
    body: str = Field(..., description="The body of the PR")


class CreatePRTool(BaseTool):
    """Tool for creating a PR."""

    name: ClassVar[str] = "create_pr"
    description: ClassVar[str] = "Create a PR for the current branch"
    args_schema: ClassVar[type[BaseModel]] = CreatePRInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, title: str, body: str) -> str:
        if self.codebase._op.git_cli.active_branch.name == self.codebase._op.default_branch:
            # If the current checked out branch is the default branch, checkout onto a new branch
            self.codebase.checkout(branch=f"{uuid.uuid4()}", create_if_missing=True)
        pr = self.codebase.create_pr(title=title, body=body)
        return pr.html_url


class GetPRContentsInput(BaseModel):
    """Input for getting PR contents."""

    pr_id: int = Field(..., description="Number of the PR to get the contents for")


class GetPRcontentsTool(BaseTool):
    """Tool for getting PR data."""

    name: ClassVar[str] = "get_pr_contents"
    description: ClassVar[str] = "Get the diff and modified symbols of a PR along with the dependencies of the modified symbols"
    args_schema: ClassVar[type[BaseModel]] = GetPRContentsInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, pr_id: int) -> str:
        modified_symbols, patch = self.codebase.get_modified_symbols_in_pr(pr_id)

        # Convert modified_symbols set to list for JSON serialization
        result = {"modified_symbols": list(modified_symbols), "patch": patch}

        return json.dumps(result, indent=2)


class CreatePRCommentInput(BaseModel):
    """Input for creating a PR comment"""

    pr_number: int = Field(..., description="The PR number to comment on")
    body: str = Field(..., description="The comment text")


class CreatePRCommentTool(BaseTool):
    """Tool for creating a general PR comment."""

    name: ClassVar[str] = "create_pr_comment"
    description: ClassVar[str] = "Create a general comment on a pull request"
    args_schema: ClassVar[type[BaseModel]] = CreatePRCommentInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(self, pr_number: int, body: str) -> str:
        self.codebase.create_pr_comment(pr_number=pr_number, body=body)
        return "Comment created successfully"


class CreatePRReviewCommentInput(BaseModel):
    """Input for creating an inline PR review comment"""

    pr_number: int = Field(..., description="The PR number to comment on")
    body: str = Field(..., description="The comment text")
    commit_sha: str = Field(..., description="The commit SHA to attach the comment to")
    path: str = Field(..., description="The file path to comment on")
    line: int | None = Field(None, description="The line number to comment on")
    side: str | None = Field(None, description="Which version of the file to comment on ('LEFT' or 'RIGHT')")
    start_line: int | None = Field(None, description="For multi-line comments, the starting line")


class CreatePRReviewCommentTool(BaseTool):
    """Tool for creating inline PR review comments."""

    name: ClassVar[str] = "create_pr_review_comment"
    description: ClassVar[str] = "Create an inline review comment on a specific line in a pull request"
    args_schema: ClassVar[type[BaseModel]] = CreatePRReviewCommentInput
    codebase: Codebase = Field(exclude=True)

    def __init__(self, codebase: Codebase) -> None:
        super().__init__(codebase=codebase)

    def _run(
        self,
        pr_number: int,
        body: str,
        commit_sha: str,
        path: str,
        line: int | None = None,
        side: str | None = None,
        start_line: int | None = None,
    ) -> str:
        self.codebase.create_pr_review_comment(
            pr_number=pr_number,
            body=body,
            commit_sha=commit_sha,
            path=path,
            line=line,
            side=side,
            start_line=start_line,
        )
        return "Review comment created successfully"


def get_workspace_tools(codebase: Codebase) -> list["BaseTool"]:
    """Get all workspace tools initialized with a codebase.

    Args:
        codebase: The codebase to operate on

    Returns:
        List of initialized Langchain tools
    """
    return [
        CommitTool(codebase),
        CreateFileTool(codebase),
        CreatePRTool(codebase),
        CreatePRCommentTool(codebase),
        CreatePRReviewCommentTool(codebase),
        DeleteFileTool(codebase),
        EditFileTool(codebase),
        GetPRcontentsTool(codebase),
        ListDirectoryTool(codebase),
        RevealSymbolTool(codebase),
        SearchTool(codebase),
        SemanticEditTool(codebase),
        ViewFileTool(codebase),
    ]
