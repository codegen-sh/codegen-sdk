from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_class_rename(tmpdir) -> None:
    # language=python
    content1 = """
my_global_var = MyClass()

def my_function(arg: MyClass | None = None):
    pass

class MyClass:
    def __init__(self):
        pass

    def my_method(self):
        pass
"""
    # language=python
    content2 = """
from file1 import MyClass

my_other_global_var = MyClass()

def my_other_function(arg: MyClass | None = None):
    pass

class MyOtherClass:
    my_attr: MyClass

    def __init__(self):
        self.my_attr = MyClass()

    def my_method(self, arg: MyClass | None = None):
        pass
"""
    # language=python
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2}) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")

        symbol = file1.get_class("MyClass")
        symbol.rename("MyRenamedClass")
        codebase.commit()

        assert (
            file1.content
            == """
my_global_var = MyRenamedClass()

def my_function(arg: MyRenamedClass | None = None):
    pass

class MyRenamedClass:
    def __init__(self):
        pass

    def my_method(self):
        pass
"""
        )
        assert (
            file2.content
            == """
from file1 import MyRenamedClass

my_other_global_var = MyRenamedClass()

def my_other_function(arg: MyRenamedClass | None = None):
    pass

class MyOtherClass:
    my_attr: MyRenamedClass

    def __init__(self):
        self.my_attr = MyRenamedClass()

    def my_method(self, arg: MyRenamedClass | None = None):
        pass
"""
        )
