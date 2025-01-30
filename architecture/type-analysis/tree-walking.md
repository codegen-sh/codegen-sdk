# Tree Walking

To compute dependencies, we have to walk the entire AST for every file.
At a high level, the procedure is pretty simple

```python
def compute_dependencies(self):
    for child in self.children:
        compute_dependencies(child)
```

We start at the root node and walk the tree until we have computed all dependencies.

## Usage Kind identification

We have to identify the kind of usage for each node. This is done by looking at the parent node and the child node.

```python
def foo() -> c:
    c()
```

We will classify the usage kind of the `c` callsite differently from the return type.

```python
class PyFunction(...):
    ...
    def _compute_dependencies(self, usage_kind: UsageKind):
        self.return_type._compute_dependencies(UsageKind.RETURN_TYPE)
        self.body._compute_dependencies(UsageKind.BODY)

```

By default, we just pass the usage kind to the children.

## Resolvable Nodes

At no step in this process described so far have we actually computed any dependencies. That's because there are some special nodes ("Resolvables") that do the heavy lifting. All of the tree walking is just to identify these nodes and the context they are used in. Resolvables are anything inheriting from `Resolvable`:

- [Name](./name-resolution.md)
- [ChainedAttribute](./chained-attribute.md)
- [SubscriptExpression](./subscript-expression.md)
- [FunctionCall](./function-call.md)
These are all processed using the [type engine](./type-engine.md) to get the definition of the node. They are then converted into an [graph-edge](./edges.md) and added to the graph.
