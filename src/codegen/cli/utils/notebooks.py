import json
from pathlib import Path
from typing import Any

DEFAULT_CELLS = [
    {
        "cell_type": "code",
        "source": """from codegen import Codebase

# Initialize codebase
codebase = Codebase('../../')

# Print out stats
print("🔍 Codebase Analysis")
print("=" * 50)
print(f"📚 Total Files: {len(codebase.files)}")
print(f"⚡ Total Functions: {len(codebase.functions)}")
print(f"🔄 Total Imports: {len(codebase.imports)}")""".strip(),
    }
]

DEMO_CELLS = [
    ##### [ CODGEN DEMO ] #####
    {"cell_type": "markdown", "source": "# Codegen Demo"},
    {
        "cell_type": "code",
        "source": """from codegen import Codebase

# Initialize FastAPI codebase
codebase = Codebase.from_repo('fastapi/fastapi')

# Print overall stats
print("🔍 FastAPI Analysis")
print("=" * 50)
print(f"📚 Total Classes: {len(codebase.classes)}")
print(f"⚡ Total Functions: {len(codebase.functions)}")
print(f"🔄 Total Imports: {len(codebase.imports)}")

# Find class with most inheritance
if codebase.classes:
    deepest_class = max(codebase.classes, key=lambda x: len(x.superclasses))
    print(f"\\n🌳 Class with most inheritance: {deepest_class.name}")
    print(f"   📊 Chain Depth: {len(deepest_class.superclasses)}")
    print(f"   ⛓️ Chain: {' -> '.join(s.name for s in deepest_class.superclasses)}")

# Find first 5 recursive functions
recursive = [f for f in codebase.functions
            if any(call.name == f.name for call in f.function_calls)][:5]
if recursive:
    print(f"\\n🔄 Recursive functions:")
    for func in recursive:
        print(f"  - {func.name} ({func.file.filepath})")""".strip(),
    },
    ##### [ TEST DRILL DOWN ] #####
    {"cell_type": "markdown", "source": "# Drilling Down on Tests"},
    {
        "cell_type": "code",
        "source": """from collections import Counter

# Filter to all test functions and classes
test_functions = [x for x in codebase.functions if x.name.startswith('test_')]

print("🧪 Test Analysis")
print("=" * 50)
print(f"📝 Total Test Functions: {len(test_functions)}")
print(f"📊 Tests per File: {len(test_functions) / len(codebase.files):.1f}")

# Find files with the most tests
print("\\n📚 Top Test Files by Count")
print("-" * 50)
file_test_counts = Counter([x.file for x in test_functions])
for file, num_tests in file_test_counts.most_common()[:5]:
    print(f"🔍 {num_tests} test classes: {file.filepath}")
    print(f"   📏 File Length: {len(file.source)} lines")
    print(f"   💡 Functions: {len(file.functions)}")""".strip(),
    },
    ##### [ TEST SPLITTING ] #####
    {"cell_type": "markdown", "source": "# Test Splitting"},
    {
        "cell_type": "code",
        "source": """print("\n📦 Splitting Test Files")
print("=" * 50)

# Process top 5 largest test files
for file, num_tests in file_test_counts.most_common()[:5]:
    # Create a new directory based on the file name
    base_name = file.path.replace('.py', '')
    print(f"\n🔄 Processing: {file.filepath}")
    print(f"   📊 {num_tests} test classes to split")

    # Move each test class to its own file
    for test_class in file.classes:
        if test_class.name.startswith('Test'):
            # Create descriptive filename from test class name
            new_file = f"{base_name}/{test_class.name.lower()}.py"
            print(f"   📝 Moving {test_class.name} -> {new_file}")

            # Codegen handles all the complexity:
            # - Creates directories if needed
            # - Updates all imports automatically
            # - Maintains test dependencies
            # - Preserves decorators and docstrings
            test_class.move_to_file(new_file)

# Commit changes to disk
codebase.commit()""".strip(),
    },
]


def create_cells(cells_data: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Convert cell data into Jupyter notebook cell format."""
    return [
        {
            "cell_type": cell["cell_type"],
            "source": cell["source"],
            "metadata": {},
            "execution_count": None,
            "outputs": [] if cell["cell_type"] == "code" else None,
        }
        for cell in cells_data
    ]


def create_notebook(jupyter_dir: Path, demo: bool = False) -> Path:
    """Create a new Jupyter notebook if it doesn't exist.

    Args:
        jupyter_dir: Directory where the notebook should be created
        demo: Whether to create a demo notebook with FastAPI example code

    Returns:
        Path to the created or existing notebook
    """
    notebook_path = jupyter_dir / ("demo.ipynb" if demo else "tmp.ipynb")
    if not notebook_path.exists():
        cells = create_cells(DEMO_CELLS if demo else DEFAULT_CELLS)
        notebook_content = {
            "cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        notebook_path.write_text(json.dumps(notebook_content, indent=2))
    return notebook_path
