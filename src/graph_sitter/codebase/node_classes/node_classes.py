from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING

from graph_sitter.core.interfaces.resolvable import Resolvable

if TYPE_CHECKING:
    from graph_sitter.core.class_definition import Class
    from graph_sitter.core.detached_symbols.code_block import CodeBlock
    from graph_sitter.core.detached_symbols.function_call import FunctionCall
    from graph_sitter.core.detached_symbols.parameter import Parameter
    from graph_sitter.core.expressions import Expression
    from graph_sitter.core.expressions.type import Type
    from graph_sitter.core.file import SourceFile
    from graph_sitter.core.function import Function
    from graph_sitter.core.import_resolution import Import
    from graph_sitter.core.statements.comment import Comment
    from graph_sitter.core.symbol import Symbol


@dataclass
class NodeClasses:
    file_cls: type[SourceFile]
    class_cls: type[Class]
    function_cls: type[Function]
    import_cls: type[Import]

    # Detached symbols
    parameter_cls: type[Parameter]
    code_block_cls: type[CodeBlock]
    function_call_cls: type[FunctionCall]
    comment_cls: type[Comment]
    bool_conversion: dict[bool, str]
    symbol_map: dict[str, type[Symbol]] = field(default_factory=dict)
    expression_map: dict[str, type[Expression]] = field(default_factory=dict)
    type_map: dict[str, type[Type] | dict[str, type[Type]]] = field(default_factory=dict)
    keywords: list[str] = field(default_factory=list)
    type_node_type: str = ""
    int_dict_key: bool = False

    @cached_property
    def resolvables(self) -> set[str]:
        id_types = {k for k, v in self.expression_map.items() if isinstance(v, type) and issubclass(v, Resolvable)}
        id_types.update(["identifier"])
        return id_types
