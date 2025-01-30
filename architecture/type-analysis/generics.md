# Generics Analysis

Analysis and resolution of generic types, type parameters, and constraints across the codebase.

## Core Functionality

### Generic Type Resolution

- Type parameter inference
- Constraint checking
- Variance analysis
- Generic type instantiation

### Examples

```python
# Python generics
from typing import TypeVar, Generic, List

T = TypeVar('T')
S = TypeVar('S', bound='BaseClass')
U = TypeVar('U', str, int)  # Union constraint

class Container(Generic[T]):
    def __init__(self, item: T):
        self.item = item

    def get(self) -> T:
        return self.item
```

```typescript
// TypeScript generics
interface Box<T> {
  value: T;
}

class Stack<T extends object> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }
}

// Complex constraints
function merge<T extends object, U extends object>(
  obj1: T,
  obj2: U
): T & U {
  return { ...obj1, ...obj2 };
}
```

## Implementation

### Generic Resolution

```python
class GenericResolver:
    def resolve_generic_type(
        self,
        base_type: Type,
        type_args: List[Type],
        constraints: List[Constraint]
    ) -> Type:
        # Validate constraints
        self.validate_constraints(type_args, constraints)

        # Create concrete type
        return self.instantiate_generic(base_type, type_args)
```

### Type Parameter Inference

```typescript
interface TypeInference {
  inferTypeParameters<T>(
    genericType: Type,
    concreteType: Type
  ): Map<TypeParameter, Type>;

  validateConstraints(
    typeArgs: Map<TypeParameter, Type>,
    constraints: Constraint[]
  ): boolean;
}
```

## Next Step

After generics analysis, the system builds [Graph Edges](./graph-edges.md) to represent relationships between types and symbols.
