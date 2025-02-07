# Incremental Computation

After we performed some changes to the codebase, we may need to recompute the codebase graph.
This is not a trivial task, because we need to be able to recompute the codebase graph incrementally and efficiently.

## Use Cases

### 1. Repeated Moves

```python
# file1.py
def foo():
    return bar()


def bar():
    return 42
```

Let's move symbol `bar` to `file2.py`

```python
# file2.py
def bar():
    return 42
```

Then we move symbol `foo` to `file3.py`

```python
# file3.py
from file2 import bar


def foo():
    return bar()
```

You'll notice we have added an import from file2, not file1. This means that before we can move foo to file3, we need to sync the graph to reflect the changes in file2.

### 2. Branching

If we want to checkout a different branch, we need to update the baseline state to the git commit of the new branch and recompute the codebase graph.

## Next Step

After understanding the overview of incremental computation, let's look at how we [detect changes](./B.%20Change%20Detection.md) in the codebase.
