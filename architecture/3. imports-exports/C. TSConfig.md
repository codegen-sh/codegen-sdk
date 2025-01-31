# TSConfig Support

Integration with TypeScript's configuration system for import resolution and module handling.

## Core Features

### Configuration Parsing

- tsconfig.json loading and inheritance
- Base URL and path mapping
- Module resolution strategies
- Project references

Example tsconfig.json:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@app/*": ["src/app/*"],
      "@shared/*": ["src/shared/*"]
    },
    "moduleResolution": "node",
    "target": "es2020",
    "module": "esnext"
  },
  "extends": "./tsconfig.base.json",
  "references": [
    { "path": "../shared" }
  ]
}
```

### Module Resolution

Path alias resolution example:

```typescript
// Original import with path alias
import { UserService } from '@app/services/user.service';

// Resolved to actual file path
import { UserService } from './src/app/services/user.service';
```

Project reference example:

```typescript
// In project A
export interface User {
  id: string;
  name: string;
}

// In project B (with reference to A)
import { User } from '@shared/types';
```

### Advanced Features

Conditional module resolution:

```json
{
  "compilerOptions": {
    "paths": {
      "@api/*": {
        "development": ["src/api/mock/*"],
        "production": ["src/api/real/*"]
      }
    }
  }
}
```

## Implementation Details

### Resolution Process

Example resolution flow:

```typescript
// Input: import statement
import { Component } from '@app/components/Button';

// 1. Parse tsconfig paths
const paths = {
  '@app/*': ['src/app/*']
};

// 2. Apply path mapping
const possiblePaths = [
  'src/app/components/Button',
  'src/app/components/Button.ts',
  'src/app/components/Button/index.ts'
];

// 3. Resolve to actual file
const resolvedPath = 'src/app/components/Button/index.ts';
```

### Performance Optimization

Cache structure example:

```typescript
interface TSConfigCache {
  configs: Map<string, ParsedTSConfig>;
  pathMappings: Map<string, ResolvedPath>;
  projectReferences: Map<string, ProjectRef>;
}

// Usage
if (cache.pathMappings.has(importPath)) {
  return cache.pathMappings.get(importPath);
}
```

### Extension Points

Custom resolver example:

```typescript
interface PathResolver {
  resolvePath(
    importPath: string,
    containingFile: string
  ): string | undefined;
}

class CustomTSConfigResolver implements PathResolver {
  resolvePath(importPath: string, containingFile: string): string | undefined {
    // Custom resolution logic
    return this.customResolve(importPath);
  }
}
```

## Next Step

After TSConfig processing is complete, the system proceeds to [Type Analysis](../4.%20type-analysis/A.%20Type%20Analysis.md) where it builds a complete understanding of types, symbols, and their relationships.
