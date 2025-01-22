from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar, override

from graph_sitter.core.autocommit import reader
from graph_sitter.core.detached_symbols.code_block import CodeBlock
from graph_sitter.core.interfaces.has_attribute import HasAttribute
from graph_sitter.core.interfaces.has_block import HasBlock
from graph_sitter.core.interfaces.has_value import HasValue
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.core.interfaces.supports_generic import SupportsGenerics
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.statements.attribute import Attribute
from graph_sitter.core.statements.statement import Statement
from graph_sitter.enums import SymbolType
from graph_sitter.writer_decorators import apidoc, noapidoc
from tree_sitter import Node as TSNode

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


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
