# Dependency Manager

Integration with language-specific package managers and dependency resolution systems.

## Core Functionality

### Package Management

- Package resolution
- Version management
- Dependency tree analysis
- Lock file handling

### Supported Systems

Python example:

```python
# requirements.txt
requests==2.28.1
pandas>=1.4.0,<2.0.0
numpy~=1.21.0

# pyproject.toml
[project]
dependencies = [
    "requests==2.28.1",
    "pandas>=1.4.0,<2.0.0",
    "numpy~=1.21.0",
]

[project.optional-dependencies]
test = [
    "pytest>=7.0.0",
    "pytest-cov>=3.0.0",
]
```

TypeScript example:

```json
// package.json
{
  "dependencies": {
    "lodash": "^4.17.21",
    "axios": "~0.27.2"
  },
  "devDependencies": {
    "typescript": "^4.8.0",
    "@types/node": "^18.0.0"
  }
}
```

## Implementation

### Dependency Resolution

```python
class DependencyResolver:
    def __init__(self):
        self.package_index = PackageIndex()
        self.dependency_cache = {}

    def resolve_dependencies(
        self,
        requirements: List[Requirement]
    ) -> DependencyTree:
        """Resolve dependencies into a concrete dependency tree."""
        resolved = DependencyTree()

        for req in requirements:
            # Find compatible versions
            versions = self.find_compatible_versions(req)

            # Check for conflicts
            if conflicts := self.check_conflicts(versions, resolved):
                raise DependencyConflict(conflicts)

            # Add to resolution
            resolved.add_requirement(req, versions.best)

        return resolved
```

### Version Management

```typescript
interface VersionManager {
  parseVersion(version: string): Version;
  satisfiesRange(version: Version, range: string): boolean;
  findBestMatch(versions: Version[], range: string): Version;
}

class SemVerManager implements VersionManager {
  findBestMatch(
    versions: Version[],
    range: string
  ): Version {
    const compatible = versions.filter(v =>
      this.satisfiesRange(v, range)
    );

    return this.selectBestVersion(compatible);
  }
}
```

## Next Step

The dependency manager works closely with the [Type Engine](./type-engine.md) to ensure type compatibility across dependencies.
