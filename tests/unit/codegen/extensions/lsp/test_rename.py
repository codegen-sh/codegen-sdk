import pytest
from lsprotocol.types import (
    Position,
    RenameParams,
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
def world():
    pass
         """.strip(),
            },
        )
    ],
)
async def test_rename(client: LanguageClient, codebase: Codebase, assert_expected):
    result = await client.text_document_rename_async(
        params=RenameParams(
            position=Position(line=0, character=0),
            text_document=TextDocumentIdentifier(uri="file://test.py"),
            new_name="world",
        )
    )

    assert_expected(codebase, check_codebase=False)
