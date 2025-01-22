"""Utilities to prevent circular imports."""

from typing import TYPE_CHECKING, Any, TypeGuard, Union

if TYPE_CHECKING:
    from graph_sitter.core.file import File
    from graph_sitter.core.import_resolution import Import
    from graph_sitter.core.symbol import Symbol


def is_file(node: Any) -> TypeGuard["File"]:
    from graph_sitter.core.file import File

    return isinstance(node, File)


def is_symbol(node: Any) -> TypeGuard["Symbol"]:
    from graph_sitter.core.symbol import Symbol

    return isinstance(node, Symbol)


def is_on_graph(node: Any) -> TypeGuard[Union["Import", "Symbol"]]:
    from graph_sitter.core.import_resolution import Import
    from graph_sitter.core.symbol import Symbol

    return isinstance(node, Import | Symbol)
