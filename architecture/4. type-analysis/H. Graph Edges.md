# Graph Edges

The SDK contains a graph of nodes and edges.
Nodes are the core of the graph and represent the symbols in the codebase. Examples include:

- Symbols: Classes, functions, Assignments, etc.
- Imports, Exports
- Files
- Parameters, Attributes
  Edges are between - each containes 4 elements:
- Source: The node that the edge is coming from
- Target: The node that the edge is going to
- Type: The type of the edge
- Metadata: Additional information about the edge

## Edge Types

We have 4 types of [edges](../src/codegen/sdk/enums.py#L10)

- IMPORT_SYMBOL_RESOLUTION: An edge from an import to a symbol
- EXPORT: An edge from a symbol to an export
- SUBCLASS: An edge from a symbol to a subclass
- SYMBOL_USAGE: An edge from a symbol to a usage

The only edges that are used in almost every API are SYMBOL_USAGE edges. They are also the only ones that have additional metadata.

## Edge construction order

To compute the graph we follow a specific order:

1. Import edges are added first
   - This is completely independent of the type engine
1. Symbol edges are added next
   - these may export symbols that are imported from other files.
   - This is almost entirely independent of the type engine
1. Subclass edges are added next
   - these may reference symbols that are imported or exported from other files.
   - This is fully dependent on the type engine
1. Usage edges are added last
   - they reference symbols that are imported or exported from other files
   - This is fully dependent on the type engine
   - Subclass edges are computed beforehand as a performance optimization

## Usages

SYMBOL_USAGE edges contain additional [metadata](../src/codegen/sdk/core/dataclasses/usage.py)

- match: The exact match of the usage
- usage_symbol: The symbol this object is used in. Derived from the match object
- usage_type: How this symbol was used. Derived from the resolution stack
- imported_by: The import that imported this symbol. Derived from the resolution stack
- kind: Where this symbol was used (IE: in a type parameter or in the body of the class, etc). Derived from the compute dependencies function
  You may notice these edges are actually between the usage symbol and the match object but the match object is not on the graph. This way we have constructed triple edges.
- They are technically edges between the usage symbol and the symbol contained in the match object
- The edge metadata contains the match object

## Next Step

After constructing the type graph, the system moves on to [Edit Operations](../5.%20performing-edits/A.%20Edit%20Operations.md) where it can safely modify code while preserving type relationships.
