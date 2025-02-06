# Graph Recomputation

## Node Reparsing

Some limitations we encounter are:

- It is non-trivial to update tree sitter nodes, and the SDK has no method to do this.
- Therefore, all existing nodes are invalidated and need to be recomputed every time filesystem state changes.

Therefore, to recompute the graph, we must first have the filesystem state updated. Then we can remove all nodes in the modified files and create new nodes in the modified files.

## Edge Recomputation

- Nodes may either use (out edges) or be used by (in edges) other nodes.
  - Recomputing the out-edges is straightforward, we just need to reparse the file and compute dependencies again.
  - Recomputing the in-edges is more difficult.
    - The basic algorithm of any incremental computation engine is to:
      - Detect what changed
      - Update that query with the new data
      - If the output of the query changed, we need to update all the queries that depend on that query.

### Detecting what changed

A difficulty is that the nodes are completely freshed for updated files. Therefore, this by default will include all nodes in updated files.

### Updating the query

To do this, we:

- Wipe the entire cache of the query engine
- Remove all existing out edges of the node
- Recompute dependencies of that node

### Update what changed

This part has not been fully implemented yet. Currently, we update all the nodes that are descendants of the changed node and all the nodes in the file.

## Next Step

After graph recomputation, the system is ready for the next set of operations. The cycle continues with [File Discovery](../plumbing/file-discovery.md) for any new changes.
