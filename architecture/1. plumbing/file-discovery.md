# File Discovery

The file discovery process is responsible for identifying and organizing all relevant files in a project that need to be processed by the SDK.

## Initialization

- We take in either a list of projects or a path to a filesystem.
- If we get a path, we'll detect the programming language, initialize the git client based on the path and get a Project

## File discovery

- We discover files using the git client so we can respect gitignored files
- We then filter files based on the language and the project configuration
  - If specified, we filter by subdirectories
  - We also filter by file extensions

## Next Step

After file discovery is complete, the files are passed to the [Tree-sitter Parsing](../parsing/tree-sitter.md) phase, where each file is parsed into a concrete syntax tree.
