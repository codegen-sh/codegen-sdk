# Architecture of the Codegen SDK

This is a technical document explaining the architecture of the Codegen SDK.

## Purpose of the SDK

This SDK is designed to accomplish a large set of use cases in one tool:

- Parsing large, enterprise-scale codebases
- Making syntax aware changes to code while respecting original formatting
- Being user-friendly and easy to use
- Able to quickly execute large scale refactorings against a codebase
- Supporting multiple languages with common abstractions
- Aware of both project structure (tsconfig.json, pyproject.toml, etc.) and language-specific structure (imports, etc.)
- Able to perform type resolution
- Responding to changes to the codebase and updating the graph

### Performance

A key problem is performance. We must be able to quickly respond to user requests on enterprise codebases (IE: renaming a symbol). However, we don't know what those requests are in advance and the scope of these requests can be quite massive (They may choose to iterate over a large number of symbols and their usages). To respond to these problems, we introduced codegen cloud. We split operations into two parts:

- A "parse" step that builds up a graph of the codebase
  - This can take a long time to complete, but it only needs to be done once
  - This computes the entire graph of the codebase
- A "run" step that performs operations on the codebase
  - This can be done quickly, but it needs to be done many times
  - This uses the graph to perform operations on the codebase

This allows us to perform operations on the codebase without having to parse it every time.

## Existing Solutions

To accomplish these goals, we can look at existing classes of solutions:

### Language Server Architecture

The immediate question is: why not use a language server? They have a lot of the same goals as codegen, but do not address many of our goals:

- Language servers can handle many of these same use cases, but they are not as performant as we need.
- Generally, language servers compute their results lazily. This doesn't work for us because we need to perform a large number of operations on the codebase.
- While the LSP protocol is powerful, it is not designed to be scriptable the way codegen is.
- In Python, many of the language servers are an aglamation of many different tools and libraries. None are very good at refactoring or offer the comprehensive set of features that codegen does.

Generally language servers parse codebases in response to user actions. This is not a good fit for us because we need to perform a large number of operations on the codebase without knowing which symbols are being changed or queried.

### Compiler Architecture

Many of the same goals can be accomplished with a compiler. C However, compilers are not as user-friendly as we need.

- They do not generally offer easy-to-use apis
- They do not focus on refactoring code after parsing
- They generally don't handle graph-updates
- They aren't common or complete in python/typescript

Generally compilers build up knowledge of the entire codebase in a single pass. This is a much better fit for our use case.

## Architecture

The codegen SDK combines aspects of both systems to accomplish our goals.
At a high level our architecture is:

1. We discover files to parse

## Processing Steps

The SDK processes code through several distinct steps:

1. [File Discovery](./1. plumbing/file-discovery.md)
   - Project structure analysis
   - File system traversal

2. [Tree-sitter Parsing](./2. parsing/A. Tree Sitter.md)
   - Initial syntax tree construction
   - Language-specific parsing rules
   - Error recovery

3. [AST Construction](./2. parsing/B. AST Construction.md)
   - Abstract syntax tree building
   - Node type assignment
   - Syntax validation

4. [Import & Export Resolution](./3. imports-exports/A. Imports.md)
   - Module dependency analysis
   - [Export Analysis](./3. imports-exports/B. Exports.md)
   - [TSConfig Support](./3. imports-exports/C. TSConfig.md)
   - Path resolution

5. [Type Analysis](./4. type-analysis/A. Type Analysis.md)
   - [Type Analysis](./4. type-analysis/A. Type Analysis.md)
   - [Tree Walking](./4. type-analysis/B. Tree Walking.md)
   - [Name Resolution](./4. type-analysis/C. Name Resolution.md)
   - [Chained Attributes](./4. type-analysis/D. Chained Attributes.md)
   - [Function Calls](./4. type-analysis/E. Function Calls.md)
   - [Generics](./4. type-analysis/F. Generics.md)
   - [Subscript Expression](./4. type-analysis/G. Subscript Expression.md)
   - [Graph Edges](./4. type-analysis/H. Graph Edges.md)

6. [Performing Edits](./5. performing-edits/A. Edit Operations.md)
   - [Transaction Manager](./5. performing-edits/B. Transaction Manager.md)
   - Change validation
   - Format preservation

7. [Incremental Computation](./6. incremental-computation/A. Overview.md)
   - [Detecting Changes](./6. incremental-computation/B. Change Detection.md)
   - [Recomputing Graph](./6. incremental-computation/C. Graph Recomputation.md)
   - Cache invalidation
