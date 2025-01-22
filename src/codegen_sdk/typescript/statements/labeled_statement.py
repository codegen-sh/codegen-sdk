from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from tree_sitter import Node as TSNode

from codegen_sdk.codebase.codebase_graph import CodebaseGraph
from codegen_sdk.core.expressions import Expression, Name
from codegen_sdk.core.interfaces.has_name import HasName
from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.statements.statement import Statement, StatementType
from codegen_sdk.writer_decorators import ts_apidoc

if TYPE_CHECKING:
    from codegen_sdk.typescript.detached_symbols.code_block import TSCodeBlock


Parent = TypeVar("Parent", bound="TSCodeBlock")


@ts_apidoc
class TSLabeledStatement(Statement[Parent], HasName, Generic[Parent]):
    """Statement with a named label. It resolves to various types of statements like loops, switch cases, etc.

    Examples:
    ```
    outerLoop: for (let i = 0; i < 5; i++) {
      innerLoop: for (let j = 0; j < 5; j++) {
        if (i === 2 && j === 2) {
          break outerLoop; // This will break out of the outer loop
        }
        console.log(`i: ${i}, j: ${j}`);
      }
    }
    ```
    ```
    emptyStatement: { pass }
    ```
    """

    statement_type = StatementType.LABELED_STATEMENT
    body: Expression | None

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: Parent, pos: int) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        self._name_node = Name(ts_node.child_by_field_name("label"), file_node_id, G, self)
        body_node = self.ts_node.child_by_field_name("body")
        self.body = self._parse_expression(body_node) if body_node else None

    @property
    def label(self) -> str:
        """Returns the label of the labeled statement.

        Acts as a property getter that returns the name of the labeled statement. For example, in code like
        'outerLoop: for...', this would return 'outerLoop'.

        Returns:
            str: The label name of the statement.
        """
        return self.name
