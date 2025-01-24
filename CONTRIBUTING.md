# Contributing to Graph Sitter

Thank you for your interest in contributing to Graph Sitter! This document outlines the process and guidelines for contributing.

## Contributor License Agreement

By contributing to Graph Sitter, you agree that:

1. Your contributions will be licensed under the project's license.
2. You have the right to license your contribution under the project's license.
3. You grant Codegen a perpetual, worldwide, non-exclusive, royalty-free license to use your contribution.

See our [CLA](CLA.md) for more details.

## Development Setup

### Installing UV Package Manager

UV is a fast Python package installer and resolver. To install:

**macOS**:
```bash
brew install uv
```

For other platforms, see the [UV installation docs](https://github.com/astral-sh/uv).

### Setting Up the Development Environment

After installing UV, set up your development environment:
```bash
uv venv
source .venv/bin/activate
uv sync --dev
```

> [!TIP]
> - If sync fails with `missing field 'version'`, you may need to delete lockfile and rerun `rm uv.lock && uv sync --dev`.
> - If sync fails with failed compilation, you may need to install clang and rerun `uv sync --dev`.

### Running Tests

```bash
# Unit tests (tests atomic functionality)
uv run pytest tests/unit -n auto

# Codemod tests (tests larger programs)
uv run pytest tests/integration/codemod/test_codemods.py -n auto
```

## Pull Request Process

1. Fork the repository and create your branch from `develop`.
2. Ensure your code passes all tests.
3. Update documentation as needed.
4. Submit a pull request to the `develop` branch.
5. Include a clear description of your changes in the PR.

## Release Process

First you must wait for all required checks to pass before releasing.
Create a git tag and push it to develop to trigger a new release:

```bash
git switch develop
git pull
git tag v0.YOUR_VERSION
git push origin v0.YOUR_VERSION
```

This will trigger a release job to build this new version.

