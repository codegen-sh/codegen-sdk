from pydantic import BaseModel, ConfigDict

from codegen.sdk.codebase.span import Span


class Placeholder(BaseModel):
    model_config = ConfigDict(frozen=True)
    preview: str
    span: Span
    kind_id: int
    name: str
