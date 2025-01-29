from __future__ import annotations

from typing import TYPE_CHECKING, Self

from openai import BaseModel
from pydantic import ConfigDict

if TYPE_CHECKING:
    from codegen.sdk.codebase.span import Span


class AST(BaseModel):
    model_config = ConfigDict(frozen=True)
    codegen_sdk_type: str
    span: Span
    tree_sitter_type: str
    children: list[tuple[str | None, Self]]
