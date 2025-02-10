import pytest
from lsprotocol.types import (
    DefinitionParams,
    Location,
    Position,
    Range,
    TextDocumentIdentifier,
)
from pytest_lsp import LanguageClient

from codegen.sdk.core.codebase import Codebase


@pytest.mark.parametrize(
    "original, position, expected_location",
    [
        (
            {
                "test.py": """
def example_function():
    pass

def main():
    example_function()
                """.strip(),
            },
            Position(line=4, character=4),  # Position of example_function call
            Location(
                uri="file://test.py",
                range=Range(
                    start=Position(line=0, character=4),
                    end=Position(line=0, character=19),
                ),
            ),
        )
    ],
)
async def test_go_to_definition(
    client: LanguageClient,
    codebase: Codebase,
    original: dict,
    position: Position,
    expected_location: Location,
):
    result = await client.text_document_definition_async(
        params=DefinitionParams(
            text_document=TextDocumentIdentifier(uri="file://test.py"),
            position=position,
        )
    )

    assert isinstance(result, Location)
    assert result.uri == expected_location.uri
    assert result.range == expected_location.range
