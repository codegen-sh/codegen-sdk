from typing import Any, Union

import pytest
from lsprotocol.types import (
    Hover,
    HoverParams,
    MarkupContent,
    Position,
    TextDocumentIdentifier,
)
from pytest_lsp import LanguageClient

from codegen.sdk.core.codebase import Codebase


@pytest.mark.parametrize(
    "original, position, expected_content",
    [
        (
            {
                "test.py": """
def example_function(param: str) -> str:
    \"\"\"Example function that returns a greeting.

    Args:
        param: Name to greet

    Returns:
        A greeting message
    \"\"\"
    return f"Hello, {param}!"

example_function("world")
                """.strip(),
            },
            Position(line=11, character=0),  # Position of example_function call
            "```python\ndef example_function(param: str) -> str\n```\n\nExample function that returns a greeting.\n\nArgs:\n    param: Name to greet\n\nReturns:\n    A greeting message",
        )
    ],
)
async def test_hover(
    client: LanguageClient,
    codebase: Codebase,
    original: dict,
    position: Position,
    expected_content: str,
):
    result = await client.text_document_hover_async(
        params=HoverParams(
            text_document=TextDocumentIdentifier(uri="file://test.py"),
            position=position,
        )
    )

    assert isinstance(result, Hover)

    def extract_content(hover_content: Union[MarkupContent, str, list[dict[str, Any]], dict[str, Any]]) -> str:
        if isinstance(hover_content, MarkupContent):
            return hover_content.value
        elif isinstance(hover_content, str):
            return hover_content
        elif isinstance(hover_content, dict):
            return hover_content.get("value", "")
        elif isinstance(hover_content, list):
            return "\n".join(item.get("value", str(item)) if isinstance(item, dict) else str(item) for item in hover_content)
        return ""

    actual_content = extract_content(result.contents)
    assert actual_content == expected_content
