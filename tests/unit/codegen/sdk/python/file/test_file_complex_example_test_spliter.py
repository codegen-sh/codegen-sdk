from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_file_complex_example_test_spliter(tmpdir) -> None:
    """Test splitting a test file into multiple files, removing unused imports"""
    # language=python
    content = """
from math import pi
from math import sqrt

def test_set_comparison():
    set1 = set("1308")
    set2 = set("8035")
    assert set1 == set2

def test_math_sqrt():
    assert sqrt(4) == 2
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        base_name = "test_utils"

        # Group tests by subpath
        test_groups = {}
        for test_function in file.functions:
            if test_function.name.startswith("test_"):
                test_subpath = "_".join(test_function.name.split("_")[:3])
                if test_subpath not in test_groups:
                    test_groups[test_subpath] = []
                test_groups[test_subpath].append(test_function)

        # Print and process each group
        for subpath, tests in test_groups.items():
            new_filename = f"{base_name}/{subpath}.py"

            # Create file if it doesn't exist
            if not codebase.has_file(new_filename):
                new_file = codebase.create_file(new_filename)
            file = codebase.get_file(new_filename)

            # Move each test in the group
            for test_function in tests:
                print(f"Moving function {test_function.name} to {new_filename}")
                test_function.move_to_file(new_file, strategy="update_all_imports", include_dependencies=True)
                original_file = codebase.get_file("test.py")

        # Force a commit to ensure all changes are applied
        codebase.commit()

        # Verify the results
        # Check that original test.py is empty of test functions
        original_file = codebase.get_file("test.py", optional=True)
        assert original_file is not None
        assert len([f for f in original_file.functions if f.name.startswith("test_")]) == 0

        # Verify test_set_comparison was moved correctly
        set_comparison_file = codebase.get_file("test_utils/test_set_comparison.py", optional=True)
        assert set_comparison_file is not None
        assert "test_set_comparison" in set_comparison_file.content
        assert 'set1 = set("1308")' in set_comparison_file.content

        # Verify test_math_sqrt was moved correctly
        math_file = codebase.get_file("test_utils/test_math_sqrt.py", optional=True)
        assert math_file is not None
        assert "test_math_sqrt" in math_file.content
        assert "assert sqrt(4) == 2" in math_file.content

        # Verify imports were preserved
        assert "from math import sqrt" in math_file.content
        assert "from math import pi" not in math_file.content  # Unused import should be removed
