from __future__ import annotations

from typing import TYPE_CHECKING

from graph_sitter.codebase.codebase_graph import CodebaseGraph
from graph_sitter.core.expressions.builtin import Builtin
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.statements.import_statement import ImportStatement
from graph_sitter.core.symbol_groups.collection import Collection
from graph_sitter.typescript.import_resolution import TSImport
from graph_sitter.writer_decorators import ts_apidoc
from tree_sitter import Node as TSNode

if TYPE_CHECKING:
    from graph_sitter.typescript.detached_symbols.code_block import TSCodeBlock


@ts_apidoc
class TSImportStatement(ImportStatement["TSFile", TSImport, "TSCodeBlock"], Builtin):
    """A class representing an import statement in TypeScript, managing both static and dynamic imports.

    This class handles various types of TypeScript imports including regular import statements,
    dynamic imports, and export statements. It provides functionality to manage and track imports
    within a TypeScript file, enabling operations like analyzing dependencies, moving imports,
    and modifying import statements.

    Attributes:
        imports (Collection): A collection of TypeScript imports contained within the statement.
    """

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: TSCodeBlock, pos: int, *, source_node: TSNode | None = None) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        imports = []
        if ts_node.type == "import_statement":
            imports.extend(TSImport.from_import_statement(ts_node, file_node_id, G, self))
        elif ts_node.type == "call_expression":
            import_call_node = ts_node.child_by_field_name("function")
            arguments = ts_node.child_by_field_name("arguments")
            imports.extend(TSImport.from_dynamic_import_statement(import_call_node, arguments, file_node_id, G, self))
        elif ts_node.type == "export_statement":
            imports.extend(TSImport.from_export_statement(source_node, file_node_id, G, self))
        self.imports = Collection(ts_node, file_node_id, G, self, delimiter="\n", children=imports)
        for imp in self.imports:
            imp.import_statement = self
