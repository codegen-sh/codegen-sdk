# Name Resolution

The name resolution system handles symbol references, scoping rules, and name binding across the codebase.

## What's in a name?

A name is a `Name` node. It is just a string of text.
For example, `foo` is a name.

```python
from my_module import foo
foo()
```

Tree sitter parses this into:

```
module [0, 0] - [2, 0]
  import_from_statement [0, 0] - [0, 25]
    module_name: dotted_name [0, 5] - [0, 14]
      identifier [0, 5] - [0, 14]
    name: dotted_name [0, 22] - [0, 25]
      identifier [0, 22] - [0, 25]
  expression_statement [1, 0] - [1, 5]
    call [1, 0] - [1, 5]
      function: identifier [1, 0] - [1, 3]
      arguments: argument_list [1, 3] - [1, 5]
```

We can map the identifier nodes to `Name` nodes.
You'll see there are actually 3 name nodes here: `foo`, `my_module`, and `foo`.

- `my_module` is the module name.
- `foo` is the name imported from the module.
- `foo` is the name of the function being called.

## Name Resolution

Name resolution is the process of resolving a name to its definition. To do this, all we need to do is

1. Get the name we're looking for. (e.g. `foo`)
2. Find the scope we're looking in. (in this case, the global file scope)
3. Recursively search the scope for the name (which will return the import).
4. Use the type engine to get the definition of the name (which will return the function definition).

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
