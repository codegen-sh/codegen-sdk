from pydantic import BaseModel, ConfigDict

from graph_sitter.codebase.span import Span


class Placeholder(BaseModel):
    model_config = ConfigDict(frozen=True)
    preview: str
    span: Span
    kind_id: int
    name: str
