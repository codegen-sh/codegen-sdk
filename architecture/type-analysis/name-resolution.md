# Name Resolution

The name resolution system handles symbol references, scoping rules, and name binding across the codebase.

## Core Components

### Scope Analysis

- Lexical scoping
- Dynamic scoping (where applicable)
- Closure handling
- Module-level scope
- Class and function scope

### Name Binding

```python
class NameResolver:
    def resolve_name(self, name: str, context: Context) -> Symbol:
        # Check local scope
        if symbol := self.check_local_scope(name, context):
            return symbol

        # Check enclosing scopes
        if symbol := self.check_enclosing_scopes(name, context):
            return symbol

        # Check imported names
        if symbol := self.check_imports(name, context):
            return symbol

        raise NameError(f"Name '{name}' is not defined")
```

## Language Features

### Python

```python
# Local vs global scope
global_var = 1

def outer():
    outer_var = 2
    def inner():
        nonlocal outer_var
        local_var = 3
        outer_var = 4  # Modifies outer_var
```

### TypeScript

```typescript
// Module scope
export const value = 'exported';

// Block scope
{
    const blockScoped = true;
    let mutable = 1;
}

// Class fields
class Example {
    private field = 'private';
    #hardPrivate = 'truly private';
    static shared = 'shared';
}
```

## Next Step

After name resolution, the system processes [Chained Attributes](./chained-attributes.md) to handle method and property access chains.
