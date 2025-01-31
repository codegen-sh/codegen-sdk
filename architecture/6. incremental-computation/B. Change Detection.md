# Change Detection

Efficient detection and analysis of changes in the codebase to drive incremental updates.

## Core Functionality

### Change Types

- File modifications
- AST changes
- Symbol changes
- Type changes
- Dependency changes

### Detection Strategies

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Set, List

class ChangeType(Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"

@dataclass
class FileChange:
    type: ChangeType
    path: str
    old_path: str = None  # For moves

@dataclass
class ASTChange:
    node_id: str
    type: ChangeType
    old_node: Optional[ASTNode] = None
    new_node: Optional[ASTNode] = None
```

## Implementation

### File Change Detection

```python
class FileChangeDetector:
    def detect_changes(
        self,
        old_files: Dict[str, FileInfo],
        new_files: Dict[str, FileInfo]
    ) -> List[FileChange]:
        changes = []

        # Detect deletions
        for path in old_files:
            if path not in new_files:
                changes.append(
                    FileChange(ChangeType.DELETED, path)
                )

        # Detect creations and modifications
        for path, new_info in new_files.items():
            if path not in old_files:
                changes.append(
                    FileChange(ChangeType.CREATED, path)
                )
            elif self.is_modified(old_files[path], new_info):
                changes.append(
                    FileChange(ChangeType.MODIFIED, path)
                )

        return changes
```

### AST Diff Computation

```typescript
interface ASTDiffer {
  computeDiff(
    oldAST: AST,
    newAST: AST
  ): ASTChanges;

  findMovedNodes(
    removedNodes: Set<ASTNode>,
    addedNodes: Set<ASTNode>
  ): Map<ASTNode, ASTNode>;
}

class TreeDiffer implements ASTDiffer {
  computeDiff(oldAST: AST, newAST: AST): ASTChanges {
    // Use tree diffing algorithm to find changes
    const changes = new ASTChanges();

    // Find structural changes
    this.findStructuralChanges(oldAST, newAST, changes);

    // Find moved nodes
    const moved = this.findMovedNodes(
      changes.removed,
      changes.added
    );

    // Update changes to reflect moves
    this.reconcileMovedNodes(changes, moved);

    return changes;
  }
}
```

## Next Step

After detecting changes, the system performs [Graph Recomputation](./C.%20Graph%20Recomputation.md) to update the dependency graph efficiently.
