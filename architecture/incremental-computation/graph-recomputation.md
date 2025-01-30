# Graph Recomputation

Efficient updating of the type and dependency graphs in response to code changes.

## Core Functionality

### Recomputation Strategy

- Partial graph updates
- Dependency propagation
- Cache invalidation
- State reconciliation

### Graph Updates

```python
from typing import Set, Dict, List
from enum import Enum

class NodeState(Enum):
    VALID = "valid"
    INVALID = "invalid"
    RECOMPUTING = "recomputing"

class DependencyGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[str]] = {}
        self.node_states: Dict[str, NodeState] = {}

    def invalidate_node(self, node_id: str):
        """Invalidate a node and its dependents."""
        self.node_states[node_id] = NodeState.INVALID
        for dependent in self.get_dependents(node_id):
            self.invalidate_node(dependent)

    def recompute_node(self, node_id: str):
        """Recompute a node's value."""
        self.node_states[node_id] = NodeState.RECOMPUTING
        node = self.nodes[node_id]

        # Ensure dependencies are valid
        for dep in self.get_dependencies(node_id):
            if self.node_states[dep] != NodeState.VALID:
                self.recompute_node(dep)

        # Recompute node value
        node.recompute()
        self.node_states[node_id] = NodeState.VALID
```

## Implementation

### Incremental Update

```typescript
interface GraphUpdater {
  invalidateNodes(changes: Changes): Set<string>;
  recomputeNodes(invalidated: Set<string>): void;
  reconcileState(): void;
}

class IncrementalGraphUpdater implements GraphUpdater {
  async updateGraph(changes: Changes): Promise<void> {
    // Find affected nodes
    const invalidated = this.invalidateNodes(changes);

    // Recompute in dependency order
    await this.recomputeNodes(invalidated);

    // Ensure graph consistency
    this.reconcileState();
  }

  private async recomputeNodes(
    nodes: Set<string>
  ): Promise<void> {
    const order = this.computeRecomputationOrder(nodes);

    for (const node of order) {
      await this.recomputeNode(node);
    }
  }
}
```

### Cache Management

```python
class CacheManager:
    def __init__(self):
        self.type_cache: Dict[str, Type] = {}
        self.symbol_cache: Dict[str, Symbol] = {}
        self.ast_cache: Dict[str, AST] = {}

    def invalidate_caches(self, changes: Changes):
        """Invalidate caches based on changes."""
        # Invalidate directly affected items
        for change in changes.files:
            self.invalidate_file_caches(change.path)

        # Invalidate dependent items
        affected = self.compute_affected_items(changes)
        for item in affected:
            self.invalidate_item_caches(item)

    def rebuild_caches(self):
        """Rebuild invalid caches."""
        self.rebuild_type_cache()
        self.rebuild_symbol_cache()
        self.rebuild_ast_cache()
```

## Next Step

After graph recomputation, the system is ready for the next set of operations. The cycle continues with [File Discovery](../plumbing/file-discovery.md) for any new changes.
