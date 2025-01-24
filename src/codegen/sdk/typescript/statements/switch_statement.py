from __future__ import annotations

from typing import TYPE_CHECKING

from tree_sitter import Node as TSNode

from codegen.sdk.core.node_id_factory import NodeId
from codegen.sdk.core.statements.switch_statement import SwitchStatement
from codegen.sdk.typescript.detached_symbols.code_block import TSCodeBlock
from codegen.sdk.typescript.statements.switch_case import TSSwitchCase
from codegen.shared.decorators.docs import ts_apidoc

if TYPE_CHECKING:
    from codegen.sdk.codebase.codebase_graph import CodebaseGraph


@ts_apidoc
class TSSwitchStatement(SwitchStatement["TSCodeBlock[Self]", "TSCodeBlock", TSSwitchCase]):
    """Typescript switch statement"""

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: TSCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        self.value = self.child_by_field_name("value")
        code_block = self.ts_node.child_by_field_name("body")
        self.cases = []
        for node in code_block.named_children:
            self.cases.append(TSSwitchCase(node, file_node_id, G, self.parent))
