from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.python import PyFile


def test_parent_statement_function(tmpdir):
    # language=python
    content = """
def foo():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        assert codebase.get_function("foo").parent_statement == file.code_block.statements[0]


def test_parent_statement_class(tmpdir):
    # language=python
    content = """
class Foo:
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        assert codebase.get_class("Foo").parent_statement == file.code_block.statements[0]


def test_parent_statement_assignment(tmpdir):
    # language=python
    content = """
foo = 1
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        assert file.get_global_var("foo").parent_statement == file.code_block.statements[0]


def test_parent_statement_nested_symbols(tmpdir):
    # language=python
    content = """
logger = get_logger()

def foo():
    class MyNestedClass:
        pass
    return MyNestedClass()

class MyClass:
    attr = 1

    def __init__(self):
        pass

if __name__ == "__main__":
    a = 1
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file: PyFile = codebase.get_file("test.py")
        assignment = file.get_global_var("logger")
        foo = file.get_function("foo")
        klass = file.get_class("MyClass")
        if_block = file.code_block.if_blocks[0]

        assert assignment.parent_statement == file.code_block.statements[0]
        assert foo.parent_statement == file.code_block.statements[1]
        assert klass.parent_statement == file.code_block.statements[2]

        # nested symbols
        assert foo.code_block.statements[0].symbol.parent_statement == foo.code_block.statements[0]
        assert klass.get_attribute("attr").assignment.parent_statement == klass.code_block.statements[0] == klass.get_attribute("attr")
        assert klass.get_method("__init__").parent_statement == klass.code_block.statements[1]
        assert if_block.consequence_block.statements[0].assignments[0].parent_statement == if_block.consequence_block.statements[0]
