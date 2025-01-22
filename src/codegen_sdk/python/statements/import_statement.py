from __future__ import annotations

from typing import TYPE_CHECKING

from tree_sitter import Node as TSNode

from codegen_sdk.codebase.codebase_graph import CodebaseGraph
from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.statements.import_statement import ImportStatement
from codegen_sdk.core.symbol_groups.collection import Collection
from codegen_sdk.python.detached_symbols.code_block import PyCodeBlock
from codegen_sdk.python.import_resolution import PyImport
from codegen_sdk.writer_decorators import py_apidoc

if TYPE_CHECKING:
    pass


@py_apidoc
class PyImportStatement(ImportStatement["PyFile", PyImport, PyCodeBlock]):
    """An abstract representation of a python import statement."""

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: PyCodeBlock, pos: int) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        imports = []
        if ts_node.type == "import_statement":
            imports.extend(PyImport.from_import_statement(ts_node, file_node_id, G, self))
        elif ts_node.type == "import_from_statement":
            imports.extend(PyImport.from_import_from_statement(ts_node, file_node_id, G, self))
        elif ts_node.type == "future_import_statement":
            imports.extend(PyImport.from_future_import_statement(ts_node, file_node_id, G, self))
        self.imports = Collection(ts_node, file_node_id, G, self, delimiter="\n", children=imports)
        for imp in self.imports:
            imp.import_statement = self
