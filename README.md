# Codegen

[![Documentation](https://img.shields.io/badge/docs-docs.codegen.com-blue)](https://docs.codegen.com)
[![Twitter Follow](https://img.shields.io/twitter/follow/codegen)](https://twitter.com/codegen)

[Codegen](https://docs.codegen.com) is a python library for manipulating codebases.

Write code that transforms code. Codegen combines the parsing power of [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) with the graph algorithms of [rustworkx](https://github.com/Qiskit/rustworkx) to enable scriptable, multi-language code manipulation at scale.

```python
from codegen import Codebase

# Codegen builds a complete graph connecting
#  functions, classes, imports and their relationships
codebase = Codebase("./")

# Work with code without dealing with syntax trees or parsing
for function in codebase.functions:
    # Comprehensive static analysis for references, dependencies, etc.
    if not function.usages:
        # Auto-handles references and imports to maintain correctness
        function.move_to_file('deprecated.py')
```

## Installation
**This library requires Python 3.12 – 3.13.**
```
uv pip install codegen
```

## Resources

- [Docs](https://docs.codegen.com)
- [Get Started](https://docs.codegen.com/introduction/getting-started)


## Why Codegen?

Software development is fundamentally programmatic. Refactoring a codebase, enforcing patterns, or analyzing control flow - these are all operations that can (and should) be expressed as programs themselves.

We built Codegen backwards from real-world refactors performed on enterprise codebases. Instead of starting with theoretical abstractions, we focused on creating APIs that match how developers actually think about code changes:

- **Natural mental model**: Write transforms that read like your thought process - "move this function", "rename this variable", "add this parameter". No more wrestling with ASTs or manual import management.

- **Battle-tested on complex codebases**: Handle Python, TypeScript, and React codebases with millions of lines of code.

- **Built for advanced intelligences**: As AI developers become more sophisticated, they need expressive yet precise tools to manipulate code. Codegen provides a programmatic interface that both humans and AI can use to express complex transformations through code itself.

## Contributing

Please see our [Contributing Guide](CONTRIBUTING.md) for instructions on how to set up the development environment and submit contributions.
