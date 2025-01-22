from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from graph_sitter._proxy import proxy_property
from graph_sitter.core.autocommit import reader
from graph_sitter.core.detached_symbols.code_block import CodeBlock
from graph_sitter.core.expressions.type import Type
from graph_sitter.core.function import Function
from graph_sitter.core.interfaces.has_attribute import HasAttribute
from graph_sitter.core.interfaces.has_block import HasBlock
from graph_sitter.core.interfaces.inherits import Inherits
from graph_sitter.core.statements.attribute import Attribute
from graph_sitter.core.symbol_groups.parents import Parents
from graph_sitter.enums import SymbolType
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import noapidoc

if TYPE_CHECKING:
    from graph_sitter.core.class_definition import Class


TCodeBlock = TypeVar("TCodeBlock", bound="CodeBlock")
TAttribute = TypeVar("TAttribute", bound="Attribute")
TFunction = TypeVar("TFunction", bound="Function")
TType = TypeVar("TType", bound="Type")


class Interface(Inherits, HasBlock, HasAttribute[TAttribute], Generic[TCodeBlock, TAttribute, TFunction, TType]):
    """Abstract representation of an Interface class.

    Attributes:
        parent_interfaces: All the interfaces that this interface extends.
    """

    symbol_type = SymbolType.Interface
    parent_interfaces: Parents[TType, Self] | None = None
    code_block: TCodeBlock

    @noapidoc
    @commiter
    def compute_superclass_dependencies(self) -> None:
        if self.parent_interfaces:
            self.parent_interfaces.compute_superclass_dependencies()

    @property
    @reader
    def attributes(self) -> list[TAttribute]:
        """List of attributes defined in this Interface."""
        raise NotImplementedError("Subclass must implement `parse`")

    @reader
    def get_attribute(self, name: str) -> TAttribute | None:
        """Returns the attribute with the given name, if it exists.

        Otherwise, returns None.
        """
        return next((x for x in self.attributes if x.name == name), None)

    @reader
    def extends(self, parent_interface: str | Interface, max_depth: int | None = None) -> bool:
        """Returns True if the interface implements the given parent interface."""
        if self.parent_interfaces is None:
            return False
        return self.parent_interfaces.is_subclass_of(parent_interface, max_depth=max_depth)

    @proxy_property
    @reader
    def implementations(self, max_depth: int | None = None) -> list[Interface | Class]:
        """Returns all classes and interfaces that implement a given interface.

        Note:
        This method can be called as both a property or a method. If used as a property, it is equivalent to invoking it without arguments.
        """
        return self._get_subclasses(max_depth)

    @noapidoc
    @reader
    @override
    def resolve_attribute(self, name: str) -> TAttribute | None:
        return self.get_attribute(name)
