# Chained Attributes

```python
class Foo:
    def foo(self):
        ...
a = Foo()
a.foo()
```

A core functionality is to be able to calculate that `a.foo()` is a usage of `foo` in the `Foo` class.
To do this, we must first understand how tree-sitter parses the code.

```
module [0, 0] - [5, 0]
  class_definition [0, 0] - [2, 11]
    name: identifier [0, 6] - [0, 9]
    body: block [1, 4] - [2, 11]
      function_definition [1, 4] - [2, 11]
        name: identifier [1, 8] - [1, 11]
        parameters: parameters [1, 11] - [1, 17]
          identifier [1, 12] - [1, 16]
        body: block [2, 8] - [2, 11]
          expression_statement [2, 8] - [2, 11]
            ellipsis [2, 8] - [2, 11]
  expression_statement [3, 0] - [3, 9]
    assignment [3, 0] - [3, 9]
      left: identifier [3, 0] - [3, 1]
      right: call [3, 4] - [3, 9]
        function: identifier [3, 4] - [3, 7]
        arguments: argument_list [3, 7] - [3, 9]
  expression_statement [4, 0] - [4, 7]
    call [4, 0] - [4, 7]
      function: attribute [4, 0] - [4, 5]
        object: identifier [4, 0] - [4, 1]
        attribute: identifier [4, 2] - [4, 5]
      arguments: argument_list [4, 5] - [4, 7]
```

If we look at this parse tree - we can see that the `a.foo()` call has a name of type attribute.  The object of the call is an identifier for `a`, and the `foo` is an attribute of the identifier for `a`. Typescript has a similar structure. These are the core building blocks of chained attributes.
Chained attributes contain 2 parts:

1. The object: `a`
2. The attribute: `foo`

All we must do to resolve the definition of `a.foo` is

1. Find the definition of the object `a` (the class `Foo`)
2. Get the attribute (`foo`) on the resolved object (`Foo`) (the function `foo`)
3. Resolve the attribute to it's original definition (in this case, the function `foo`)

## Step 1: Resolve the object

We can resolve the object by calling resolved_types to get potential types of the object.
If it is a name (like `a`) we can use the name resolution to get the definition of the name.
If it is another chained attribute, we can recursively resolve the chained attribute.
If the original type is a union, we can operate on multiple types and return all the possible results.

## Step 2: Get the attribute

We can get the attribute by calling resolve_attribute on the resolved object. Nodes which implement this inherit from `HasAttribute`. Examples include:

- Class
- File
- Type aliases
- Enums

## Step 3: Resolve the attribute

Finally, we can resolve the attribute by calling resolved_types on the attribute. This is useful in cases, particularly for attributes of the class like the following:

```python
def fuzz():
    ...

class Foo:
    foo = fuzz

a = Foo()
a.foo()
```

We can resolve the attribute by calling resolved_types on the attribute to go from the attribute (foo) to the underlying resolved type (fuzz).

## Next Step

After handling chained attributes, the system moves on to [Function Calls](./E.%20Function%20Calls.md) analysis for handling function and method invocations.
