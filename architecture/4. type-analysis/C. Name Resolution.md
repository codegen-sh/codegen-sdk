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
1. Find the scope we're looking in. (in this case, the global file scope)
1. Recursively search the scope for the name (which will return the node corresponding `from my_module import foo`).
1. Use the type engine to get the definition of the name (which will return the function definition).

## Scoping

```python
# Local vs global scope
from my_module import foo, bar, fuzz


def outer():
    def foo(): ...

    foo()
    bar()
    fuzz()

    def fuzz(): ...
```

If we wanted to resolve `foo` in this case, we would start at the name foo, then check it's parent recursively till we arrive at the function outer. We would then check for the name foo and find there is a nested function with that name. We would then return the function definition.
However, if we wanted to resolve `bar`, we would then check for the name bar and find there is no nested function, variable, or parameter with that name. We would then return the import statement.
Finally for fuzz, when we check for the name fuzz, we would find there is a nested function with that name, but it is defined after the call to `fuzz()`. We would then return the import.

## Next Step

These simple cases let us build up to more complex cases. [Chained Attributes](./D.%20Chained%20Attributes.md) covers how we handle method and property access chains.
