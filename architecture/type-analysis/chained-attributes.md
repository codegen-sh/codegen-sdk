# Chained Attributes

Analysis of method and property access chains, handling complex attribute access patterns and method chaining.

## Core Functionality

### Chain Analysis

- Method chain detection
- Property access resolution
- Type propagation through chains
- Builder pattern support

### Examples

```python
# Python method chains
(df.groupby('column')
   .filter(lambda x: x['value'] > 0)
   .transform(func)
   .reset_index())

# Builder pattern
(ConfigBuilder()
    .with_name('example')
    .with_timeout(30)
    .with_retries(3)
    .build())
```

```typescript
// TypeScript chains
user.profile
    .getSettings()
    .updateTheme('dark')
    .save()
    .then(result => console.log(result));

// jQuery-style chaining
element
    .addClass('active')
    .removeClass('hidden')
    .fadeIn()
    .css({ color: 'red' });
```

## Implementation

### Chain Resolution

```python
class ChainResolver:
    def resolve_chain(self, node: ChainNode) -> Type:
        current_type = self.resolve_base(node.base)

        for attr in node.chain:
            # Resolve each attribute in the chain
            current_type = self.resolve_attribute(current_type, attr)

        return current_type
```

### Type Propagation

```typescript
interface ChainContext {
  baseType: Type;
  intermediateTypes: Type[];
  finalType: Type;
}

class ChainAnalyzer {
  analyzeChain(chain: MethodChain): ChainContext {
    // Analyze and propagate types through the chain
    return {
      baseType: this.getBaseType(chain),
      intermediateTypes: this.getIntermediateTypes(chain),
      finalType: this.getFinalType(chain)
    };
  }
}
```

## Next Step

After handling chained attributes, the system moves on to [Generics](./generics.md) analysis for handling generic types and type parameters.
