import logging
from typing import TYPE_CHECKING, Self, TypeVar, override

from tree_sitter import Node as TSNode

from codegen_sdk.core.autocommit import writer
from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.expressions.string import String
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.core.interfaces.has_attribute import HasAttribute
from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.symbol_groups.dict import Dict, Pair
from codegen_sdk.extensions.autocommit import reader
from codegen_sdk.writer_decorators import apidoc, noapidoc, ts_apidoc

if TYPE_CHECKING:
    from codegen_sdk.codebase.codebase_graph import CodebaseGraph

Parent = TypeVar("Parent", bound="Editable")
TExpression = TypeVar("TExpression", bound=Expression)

logger = logging.getLogger(__name__)


@ts_apidoc
class TSPair(Pair):
    """A TypeScript pair node that represents key-value pairs in object literals.

    A specialized class extending `Pair` for handling TypeScript key-value pairs,
    particularly in object literals. It provides functionality for handling both
    regular key-value pairs and shorthand property identifiers, with support for
    reducing boolean conditions.

    Attributes:
        shorthand (bool): Indicates whether this pair uses shorthand property syntax.
    """

    shorthand: bool

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent)
        self.shorthand = ts_node.type == "shorthand_property_identifier"

    def _get_key_value(self) -> tuple[Expression[Self] | None, Expression[Self] | None]:
        from codegen_sdk.typescript.function import TSFunction

        key, value = None, None

        if self.ts_node.type == "pair":
            key = self.child_by_field_name("key")
            value = self.child_by_field_name("value")
            if TSFunction.is_valid_node(value.ts_node):
                value = self._parse_expression(value.ts_node)
        elif self.ts_node.type == "shorthand_property_identifier":
            key = value = self._parse_expression(self.ts_node)
        elif TSFunction.is_valid_node(self.ts_node):
            value = self._parse_expression(self.ts_node)
            key = value.get_name()
        else:
            return super()._get_key_value()
        return key, value

    @writer
    def reduce_condition(self, bool_condition: bool, node: Editable | None = None) -> None:
        """Reduces an editable to the following condition"""
        if self.shorthand and node == self.value:
            # Object shorthand
            self.parent[self.key.source] = self.G.node_classes.bool_conversion[bool_condition]
        else:
            super().reduce_condition(bool_condition, node)


@apidoc
class TSDict(Dict, HasAttribute):
    """A typescript dict object. You can use standard operations to operate on this dict (IE len, del, set, get, etc)"""

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent, delimiter: str = ",", pair_type: type[Pair] = TSPair) -> None:
        super().__init__(ts_node, file_node_id, G, parent, delimiter=delimiter, pair_type=pair_type)

    def __getitem__(self, __key: str) -> TExpression:
        for pair in self._underlying:
            pair_match = None

            if isinstance(pair, Pair):
                if isinstance(pair.key, String):
                    if pair.key.content == str(__key):
                        pair_match = pair
                elif pair.key is not None:
                    if pair.key.source == str(__key):
                        pair_match = pair

                if pair_match:
                    if pair_match.value is not None:
                        return pair_match.value
                    else:
                        return pair_match.key
        raise KeyError(f"Key {__key} not found in {list(self.keys())} {self._underlying!r}")

    def __setitem__(self, __key: str, __value: TExpression) -> None:
        new_value = __value.source if isinstance(__value, Editable) else str(__value)
        for pair in self._underlying:
            pair_match = None

            if isinstance(pair, Pair):
                if isinstance(pair.key, String):
                    if pair.key.content == str(__key):
                        pair_match = pair
                elif pair.key is not None:
                    if pair.key.source == str(__key):
                        pair_match = pair

                if pair_match:
                    # CASE: {a: b}
                    if not pair_match.shorthand:
                        if __key == new_value:
                            pair_match.edit(f"{__key}")
                        else:
                            pair.value.edit(f"{new_value}")
                    # CASE: {a}
                    else:
                        if __key == new_value:
                            pair_match.edit(f"{__key}")
                        else:
                            pair_match.edit(f"{__key}: {new_value}")
                    break
        # CASE: {}
        else:
            if not self.G.node_classes.int_dict_key:
                try:
                    int(__key)
                    __key = f"'{__key}'"
                except ValueError:
                    pass
            if __key == new_value:
                self._underlying.append(f"{__key}")
            else:
                self._underlying.append(f"{__key}: {new_value}")

    @reader
    @noapidoc
    @override
    def resolve_attribute(self, name: str) -> "Expression | None":
        return self.get(name, None)
