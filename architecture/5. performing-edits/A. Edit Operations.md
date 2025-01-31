# Edit Operations

Safe and consistent code modifications while preserving syntax, formatting, and semantic relationships.

## Core Operations

### Basic Operations

- Insert code
- Delete code
- Replace code
- Move code
- Format preservation

### Examples

```python
# Original code
def old_function(param):
    return param + 1

# Edit operation: Rename function and add type hints
def new_function(param: int) -> int:
    return param + 1

# Edit operation: Add parameter with default
def new_function(param: int, offset: int = 0) -> int:
    return param + offset
```

```typescript
// Original code
interface User {
  name: string;
}

// Edit operation: Add property
interface User {
  name: string;
  email: string;  // Added property
}

// Edit operation: Add generic parameter
interface User<T extends Record<string, unknown>> {
  name: string;
  email: string;
  metadata: T;
}
```

## Implementation

### Edit Manager

```python
class EditManager:
    def __init__(self):
        self.transaction = None
        self.history: List[Edit] = []

    def start_transaction(self):
        self.transaction = Transaction()

    def add_edit(self, edit: Edit):
        if not self.transaction:
            raise ValueError("No active transaction")
        self.transaction.add_edit(edit)

    def commit(self):
        if not self.transaction:
            return
        self.apply_edits(self.transaction.edits)
        self.history.append(self.transaction)
        self.transaction = None
```

### Format Preservation

```typescript
interface FormatPreserver {
  preserveIndentation(edit: Edit): void;
  preserveLineBreaks(edit: Edit): void;
  preserveComments(edit: Edit): void;
}

class EditFormatter implements FormatPreserver {
  formatEdit(edit: Edit): FormattedEdit {
    return {
      ...edit,
      indentation: this.computeIndentation(edit),
      lineBreaks: this.preserveLineBreaks(edit),
      comments: this.preserveComments(edit)
    };
  }
}
```

## Next Step

After preparing edits, they are managed by the [Transaction Manager](./B.%20Transaction%20Manager.md) to ensure consistency and atomicity.
