from typing import Annotated, Any

from graph_sitter.writer_decorators import apidoc
from pydantic import BaseModel, ConfigDict, PlainSerializer, PlainValidator, WithJsonSchema
from pydantic_core.core_schema import ValidationInfo
from tree_sitter import Point, Range


def validate_range(value: Any, info: ValidationInfo) -> Range:
    if isinstance(value, dict):
        value = Range(
            start_byte=value["start_byte"],
            end_byte=value["end_byte"],
            start_point=Point(**value["start_point"]),
            end_point=Point(**value["end_point"]),
        )
    elif not isinstance(value, Range):
        raise ValueError("Invalid type for range field. Expected tree_sitter.Range or dict.")
    return value


RangeAdapter = Annotated[
    Range,
    PlainValidator(validate_range),
    PlainSerializer(
        lambda range: {
            "start_byte": range.start_byte,
            "end_byte": range.end_byte,
            "start_point": {
                "row": range.start_point.row,
                "column": range.start_point.column,
            },
            "end_point": {
                "row": range.end_point.row,
                "column": range.end_point.column,
            },
        }
    ),
    WithJsonSchema(
        {
            "type": "object",
            "properties": {
                "start_byte": {"type": "integer"},
                "end_byte": {"type": "integer"},
                "start_point": {
                    "type": "object",
                    "properties": {
                        "row": {"type": "integer"},
                        "column": {"type": "integer"},
                    },
                },
                "end_point": {
                    "type": "object",
                    "properties": {"row": {"type": "integer"}, "column": {"type": "integer"}},
                },
            },
        }
    ),
]


@apidoc
class Span(BaseModel):
    """Range within the codebase"""

    model_config = ConfigDict(frozen=True)
    range: RangeAdapter
    filepath: str
