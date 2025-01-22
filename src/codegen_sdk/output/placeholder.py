from graph_sitter.codebase.span import Span
from pydantic import BaseModel, ConfigDict


class Placeholder(BaseModel):
    model_config = ConfigDict(frozen=True)
    preview: str
    span: Span
    kind_id: int
    name: str
