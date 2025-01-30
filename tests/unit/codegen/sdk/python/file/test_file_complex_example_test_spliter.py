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
        print("*" * 50)
        print("test_groups", test_groups)

        # Print and process each group
        for subpath, tests in test_groups.items():
            print(f"\n{subpath}/")
            new_filename = f"{base_name}/{subpath}.py"

            # Create file if it doesn't exist
            if not codebase.has_file(new_filename):
                new_file = codebase.create_file(new_filename)
            file = codebase.get_file(new_filename)

            # Move each test in the group
            for test_function in tests:
                print(f"    - {test_function.name}")
                test_function.move_to_file(new_file, strategy="add_back_edge")
        print("codebase.files: ", codebase.files)
        assert False
