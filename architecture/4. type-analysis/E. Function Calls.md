# Function Call

At a first glance, function calls are simple. We can resolve the function call by looking up the function name in the current scope.

However, there are some complexities to consider.

## Constructors

In Python, we can call a class definition as if it were a function. This is known as a constructor.

```python
class Foo:
    def __init__(self):
        ...

a = Foo()
```

This changes the behavior of the function call from the name. The name resolves to Foo (the class definition) but the constructor resolves to the function definition.

## Imports

```typescript
require('foo')
```

In this case, we need to resolve the import statement to the module definition.

## Return Types

```python
class Foo:
    def foo(self) -> int:
        return 1
class Bar():
    def bar(self) -> Foo:
        ...

a = Bar()
a.bar().foo()
```

In this case, we need to resolve the return type of the function to the type of the return value. However, the function definition is not the same as the return type. This means we now have 3 different things going on with function calls:

1. Resolving the function definition
2. Resolving the return type
3. Computing what this function call depends on (both the function definition and the arguments passed to the function)

## Generics

```python

def foo[T](a: list[T]) -> T:
    ...
foo([1, 2, 3])
```

Generics depend on the types of the arguments to the function. We need to resolve the types of the arguments to the function to determine the type of the generic. [Generics](./F.%20Generics.md) covers how we handle generics.

## Next Step

After understanding function calls, let's look at how we handle [Generics](./F.%20Generics.md) in the type system.
