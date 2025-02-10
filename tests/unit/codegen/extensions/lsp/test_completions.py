from lsprotocol.types import (
    CompletionParams,
    Position,
    TextDocumentIdentifier,
)
from pytest_lsp import (
    LanguageClient,
)


async def test_completion(client: LanguageClient):
    result = await client.text_document_completion_async(
        params=CompletionParams(
            position=Position(line=5, character=23),
            text_document=TextDocumentIdentifier(uri="file:///path/to/test/project/root/test_file.rst"),
        )
    )

    assert len(result.items) > 0
