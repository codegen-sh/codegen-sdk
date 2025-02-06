# Change Detection

## Lifecycle of an operation on the codebase graph

Changes will go through 4 states. By default, we do not apply changes to the codebase graph, only to the filesystem.

### Pending transactions

After calling an edit or other transaction method, the changes are stored in a pending transaction. Pending transactions will be committed as described in the previous chapter.

### Pending syncs

After a transaction is committed, the file is marked as a pending sync. This means the filesystem state has been updated, but the codebase graph has not been updated yet.

### Applied syncs

When we sync the graph, we apply all the pending syncs and clear them. The codebase graph is updated to reflect the changes. We track all the applied syncs in the codebase graph.

### Saved/baseline state

Finally, we can set the baseline state to a git commit. This is the state we target when we reset the codebase graph. When we checkout branches, we update the baseline state.

## Change Detection

When we sync or build the graph, first we build a list of all files in 3 categories:

- Removed files
- Added files
- Files to repase

For example, if we move a file, it will be in the added and removed files
If we add a file, it will be in the added files even if we peformed edits on it later.

## Codebase.commit logic

We follow the following logic

1. Commit all pending transactions
1. Write all buffered files to the disk
1. Store this to pending changes (usually we will skip the remaining steps if we commit without syncing the graph)
1. Build list of removed, added and modified files from pending changes
1. For removed files, we need to remove all the edges that point to the file.
1. For added files, we need to add all the edges that point to the file.
1. For modified files, we remove all the edges that point to the file and add all the edges that point to the new file. This is complicated since edges may pass through the modified file and need to be intelligently updated.
1. Mark all pending changes as applied

## Reset logic

Reset is just the inverse of commit. We need to

1. Cancel all pending transactions
1. Restore file state to the state to the target git commit
1. Clear all pending changes to the graph
1. Reverse all applied syncs to the graph

## Next Step

After detecting changes, the system performs [Graph Recomputation](./C.%20Graph%20Recomputation.md) to update the dependency graph efficiently.
