from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar, override

from tree_sitter import Node as TSNode

from codegen_sdk.core.autocommit import reader
from codegen_sdk.core.detached_symbols.code_block import CodeBlock
from codegen_sdk.core.interfaces.has_attribute import HasAttribute
from codegen_sdk.core.interfaces.has_block import HasBlock
from codegen_sdk.core.interfaces.has_value import HasValue
from codegen_sdk.core.interfaces.importable import Importable
from codegen_sdk.core.interfaces.supports_generic import SupportsGenerics
from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.statements.attribute import Attribute
from codegen_sdk.core.statements.statement import Statement
from codegen_sdk.enums import SymbolType
from codegen_sdk.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    from codegen_sdk.codebase.codebase_graph import CodebaseGraph


TCodeBlock = TypeVar("TCodeBlock", bound="CodeBlock")
TAttribute = TypeVar("TAttribute", bound="Attribute")
Parent = TypeVar("Parent", bound="HasBlock")


@apidoc
class TypeAlias(SupportsGenerics, HasValue, HasBlock, HasAttribute[TAttribute], Generic[TCodeBlock, TAttribute]):
    """Abstract representation of a Type object.

    Only applicable for some programming languages like TypeScript.
    """

    symbol_type = SymbolType.Interface
    code_block: TCodeBlock

    def __init__(
        self,
        ts_node: TSNode,
        file_node_id: NodeId,
        G: CodebaseGraph,
        parent: Statement[CodeBlock[Parent, ...]],
    ) -> None:
        super().__init__(ts_node, file_node_id, G, parent)
        value_node = self.ts_node.child_by_field_name("value")
        self._value_node = self._parse_type(value_node) if value_node else None
        self.type_parameters = self.child_by_field_name("type_parameters")

    @property
    @abstractmethod
    @reader
    def attributes(self) -> list[TAttribute]:
        """List of expressions defined in this Type object."""

    @reader
    def get_attribute(self, name: str) -> TAttribute | None:
        """Get attribute by name."""
        return next((x for x in self.attributes if x.name == name), None)

    @noapidoc
    @reader
    @override
    def resolve_attribute(self, name: str) -> TAttribute | None:
        return self.get_attribute(name)

    @property
    @noapidoc
    def descendant_symbols(self) -> list[Importable]:
        return super().descendant_symbols + self.value.descendant_symbols
