"""Utilities to prevent circular imports."""

from typing import TYPE_CHECKING, Any, TypeGuard, Union

if TYPE_CHECKING:
    from codegen_sdk.core.file import File
    from codegen_sdk.core.import_resolution import Import
    from codegen_sdk.core.symbol import Symbol


def is_file(node: Any) -> TypeGuard["File"]:
    from codegen_sdk.core.file import File

    return isinstance(node, File)


def is_symbol(node: Any) -> TypeGuard["Symbol"]:
    from codegen_sdk.core.symbol import Symbol

    return isinstance(node, Symbol)


def is_on_graph(node: Any) -> TypeGuard[Union["Import", "Symbol"]]:
    from codegen_sdk.core.import_resolution import Import
    from codegen_sdk.core.symbol import Symbol

    return isinstance(node, Import | Symbol)
