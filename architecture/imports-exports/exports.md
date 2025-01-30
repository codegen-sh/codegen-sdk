# Export Analysis

The export analysis system handles how modules expose their functionality to other modules in the codebase.

## Core Functionality

### Export Types

Examples of different export types:

```typescript
// Named exports
export const name = 'value';
export function func() {}
export class MyClass {}

// Default exports
export default class MainClass {}
export default function() {}
export default 'value';

// Re-exports
export { name, type } from './other-module';
export * from './module';
export { default as alias } from './module';

// Type exports
export type MyType = string | number;
export interface MyInterface {}
```

```python
# Python exports
# In __init__.py
from .module import MyClass
from .utils import utility_function

__all__ = ['MyClass', 'utility_function']

# Namespace exports
from . import submodule
from .constants import *
```

### Export Resolution

Example of export resolution:

```typescript
// Export resolution process
interface ExportGraph {
  // Track direct exports
  directExports: Map<string, Set<string>>;
  // Track re-exports
  reExports: Map<string, Map<string, string>>;
  // Track export visibility
  visibility: Map<string, 'public' | 'internal'>;
}

class ExportResolver {
  resolveExport(
    modulePath: string,
    exportName: string
  ): ResolvedExport | null {
    // Check direct exports
    if (this.isDirectExport(modulePath, exportName)) {
      return this.resolveDirectExport(modulePath, exportName);
    }

    // Check re-exports
    return this.resolveReExport(modulePath, exportName);
  }
}
```

### Language-Specific Features

Python export examples:

```python
# __all__ specification
__all__ = ['public_function', 'PublicClass']

def public_function():
    pass

def _private_function():  # Not exported
    pass

class PublicClass:
    pass

# Package exports
from .models import User
from .services import UserService
```

TypeScript export examples:

```typescript
// Barrel file (index.ts)
export * from './user.model';
export * from './user.service';
export { default as UserComponent } from './user.component';

// CommonJS exports
module.exports = {
  UserService: require('./user.service'),
  createUser: require('./user.factory')
};
```

## Implementation Details

### Analysis Process

```python
class ExportAnalyzer:
    def analyze_exports(self, module_path: str) -> ModuleExports:
        exports = ModuleExports()

        # Parse explicit exports
        explicit = self.parse_explicit_exports(module_path)
        exports.add_explicit(explicit)

        # Parse implicit exports
        implicit = self.parse_implicit_exports(module_path)
        exports.add_implicit(implicit)

        # Resolve re-exports
        reexports = self.resolve_reexports(module_path)
        exports.add_reexports(reexports)

        return exports
```

### Performance Optimization

```typescript
interface ExportCache {
  moduleExports: Map<string, Set<string>>;
  symbolTable: Map<string, SymbolInfo>;
  exportGraph: Map<string, Set<string>>;
}

class CachedExportAnalyzer {
  private cache: ExportCache;

  getExports(modulePath: string): Set<string> {
    if (this.cache.moduleExports.has(modulePath)) {
      return this.cache.moduleExports.get(modulePath)!;
    }

    const exports = this.analyzeExports(modulePath);
    this.cache.moduleExports.set(modulePath, exports);
    return exports;
  }
}
```

### Extension Points

```typescript
interface ExportTransformer {
  transformExport(
    exportName: string,
    modulePath: string
  ): TransformedExport;
}

class CustomExportHandler implements ExportTransformer {
  transformExport(
    exportName: string,
    modulePath: string
  ): TransformedExport {
    // Custom export transformation logic
    return {
      name: this.transformName(exportName),
      visibility: this.computeVisibility(modulePath)
    };
  }
}

```

## Next Step

After export analysis is complete, for TypeScript projects, the system processes [TSConfig](./tsconfig.md) configurations. Then it moves on to [Type Analysis](../type-analysis/type-analysis.md) to build a complete understanding of types and symbols.
