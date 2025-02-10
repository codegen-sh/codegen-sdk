import pytest
from lsprotocol.types import (
    CompletionParams,
    Position,
    TextDocumentIdentifier,
)
from pytest_lsp import (
    LanguageClient,
)

from codegen.sdk.core.codebase import Codebase


@pytest.mark.parametrize(
    "original, expected",
    [
        (
            {
                "test.py": """
def hello():
    pass
         """.strip(),
            },
            {
                "test.py": """
def hello():
    pass
         """.strip(),
            },
        )
    ],
)
async def test_completion(client: LanguageClient, codebase: Codebase, assert_expected):
    result = await client.text_document_completion_async(
        params=CompletionParams(
            position=Position(line=5, character=23),
            text_document=TextDocumentIdentifier(uri="file://test.py"),
        )
    )

    assert len(result.items) > 0
    assert_expected(codebase, check_codebase=False)
