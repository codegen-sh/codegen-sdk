from typing import Callable

import pytest
from lsprotocol.types import CompletionList, CompletionParams, Position, TextDocumentIdentifier
from pytest_lsp import (
    LanguageClient,
)

from codegen.sdk.core.codebase import Codebase


@pytest.mark.parametrize(
    "original, position, expected_completions",
    [
        (
            {
                "test.py": """
def hello():
    pass
hel
         """.strip(),
            },
            Position(line=5, character=23),
            ["hello"],
        )
    ],
)
async def test_completion(client: LanguageClient, codebase: Codebase, position: Position, expected_completions: list[str], assert_expected: Callable):
    result = await client.text_document_completion_async(
        params=CompletionParams(
            position=position,
            text_document=TextDocumentIdentifier(uri="file://test.py"),
        )
    )
    assert isinstance(result, CompletionList)

    assert len(result.items) > 0
    assert_expected(codebase, check_codebase=False)
