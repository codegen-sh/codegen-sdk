# Tree-sitter Parsing

Tree-sitter is used as the primary parsing engine for converting source code into concrete syntax trees. Tree-sitter supports two modes of operation:

```python
def my_function():
    pass
```

Tree sitter parses this as the following:

```
module [0, 0] - [3, 0]
  function_definition [0, 0] - [1, 8]
    name: identifier [0, 4] - [0, 15]
    parameters: parameters [0, 15] - [0, 17]
    body: block [1, 4] - [1, 8]
      pass_statement [1, 4] - [1, 8]
```

- An CST mode which includes syntax nodes (for example, the `def` keyword, spaces, or parentheses). The syntax nodes are "anonymous" and don't have any semantic meaning.
  - You don't see these nodes in the tree-sitter output, but they are there.
- A AST mode where we only focus on the semantic nodes (for example, the `my_function` identifier, and the `pass` statement). These are 'named nodes' and have semantic meaning.
  - This is different from field names (like 'body'). These mean nothing about the node, they indicate what role the child node ('block') plays in the parent node ('function_definition').

## Implementation Details

- We construct a mapping between file type and the tree-sitter grammar
- For each file given to us (via git), we parse it using the appropriate grammar

## Next Step

Once the concrete syntax trees are built, they are transformed into our abstract syntax tree representation in the [AST Construction](./ast-construction.md) phase.
