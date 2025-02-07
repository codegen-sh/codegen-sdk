from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.class_definition import Class


def test_import_rename_usage_with_alias(tmpdir) -> None:
    # language=python
    content1 = """
from file1 import foo1, foo2
from file2 import bar1, bar2
import os
import sys


class MyClass:
    def __init__(self, value):
        self.value = value

    def display_value(self):
        print(f"Value: {self.value}")

    def calculate_sum(self, a, b):
        result = a + b
        print(f"Sum: {result}")
        return result

    def file_operations(self, filename):
        try:
            with open(filename, 'r') as file:
                data = file.read()
                print(f"File contents: {data}")
        except FileNotFoundError as e:
            print(f"Error: {e}")


def foo():
    a = 1
    b = 2
    # Function call to foo1
    foo1()
    # Function call to bar1
    bar1()
    # String and list operations
    string_sample = "Hello, World!"
    list_sample = [1, 2, 3, 4, 5]
    # Join operation on list
    joined_string = ', '.join(map(str, list_sample))
    # Print joined string
    print(joined_string)

    # Using os to get current working directory
    cwd = os.getcwd()
    print(f"Current directory: {cwd}")

    # Using sys to get python version
    py_version = sys.version
    print(f"Python version: {py_version}")

    # Simulating function call on integer type, will cause an error
    try:
        a()
    except TypeError as e:
        print(f"Error: {e}")

    return b


# Create an instance of MyClass and use its methods
my_instance = MyClass(10)
my_instance.display_value()
my_instance.calculate_sum(5, 7)
my_instance.file_operations('example.txt')
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1}) as codebase:
        for imp in codebase.imports:
            codebase.log(imp)
        for symbol in codebase.symbols:
            codebase.log(symbol)
            if hasattr(symbol, "code_block"):
                for statement in symbol.code_block.statements:
                    codebase.log(statement)
            if isinstance(symbol, Class):
                for method in symbol.methods:
                    codebase.log(method)
                    for statement in method.code_block.statements:
                        codebase.log(statement)
        for file in codebase.files:
            codebase.log(file)
            for statement in file.code_block.statements:
                codebase.log(statement)
