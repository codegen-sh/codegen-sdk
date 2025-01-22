import pytest

from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.detached_symbols.argument import Argument
from graph_sitter.core.statements.expression_statement import ExpressionStatement
from graph_sitter.core.statements.return_statement import ReturnStatement
from graph_sitter.core.statements.statement import StatementType
from graph_sitter.python import PyAssignment
from graph_sitter.python.detached_symbols.decorator import PyDecorator
from graph_sitter.python.statements.if_block_statement import PyIfBlockStatement


def test_function_calls_from_file(tmpdir):
    # language=python
    content = """
from some_file import x, y, z

def foo():
    return bar()

def bar():
    def random():
        return random.randint(0, 100)
    return random()

if __name__ == "__main__":
    print(foo())
    print(bar())
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        fcalls = file.function_calls

        assert set(f.name for f in fcalls) == {"foo", "bar", "random", "randint", "print"}
        assert len(fcalls) == 7
        fcall_parents = [(f.name, type(f.parent)) for f in file.function_calls]
        assert fcall_parents == [
            ("bar", ReturnStatement),
            ("randint", ReturnStatement),
            ("random", ReturnStatement),
            ("print", ExpressionStatement),
            ("foo", Argument),
            ("print", ExpressionStatement),
            ("bar", Argument),
        ]


def test_function_calls_from_class(tmpdir):
    # language=python
    content = """
from some_file import bar

class A:
    attr = bar()

    def __init__(self):
        self.attr = self.foo()

    def foo(self):
        return bar()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        fcalls = file.get_class("A").function_calls

        assert set(f.name for f in fcalls) == {"bar", "foo"}
        assert len(fcalls) == 3
        # Unpack each function call's properties for assertion
        first_call = file.function_calls[0]
        second_call = file.function_calls[1]
        third_call = file.function_calls[2]

        # Assertions for the first function call
        assert first_call.parent.parent.parent.level == 1
        assert first_call.name == "bar"
        assert first_call.parent.parent.statement_type == StatementType.CLASS_ATTRIBUTE

        # Assertions for the second function call
        assert second_call.parent.parent.parent.level == 2
        assert second_call.name == "foo"
        assert second_call.parent.parent.statement_type == StatementType.ASSIGNMENT

        # Assertions for the third function call
        assert third_call.parent.parent.level == 2
        assert third_call.name == "bar"
        assert third_call.parent.statement_type == StatementType.RETURN_STATEMENT


def test_function_calls_from_decorated_definitions(tmpdir):
    # language=python
    content = """
@pytest.mark.parametrize("x", [1, 2, 3])
def foo():
    return bar()

@my_decorator()
@my_decorator2(a=1, b=2, c=d())
class A:
    def __init__(self):
        self.attr = self.foo()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        func_fcalls = file.get_function("foo").function_calls
        class_fcalls = file.get_class("A").function_calls

        assert set(f.name for f in func_fcalls) == {"bar", "parametrize"}
        assert set(f.name for f in class_fcalls) == {"foo", "my_decorator", "my_decorator2", "d"}
        assert len(func_fcalls) == 2
        assert len(class_fcalls) == 4

        func_fcall_parents = [(f.name, type(f.parent)) for f in func_fcalls]
        class_fcall_parents = [(f.name, type(f.parent)) for f in class_fcalls]
        assert func_fcall_parents == [
            ("parametrize", PyDecorator),
            ("bar", ReturnStatement),
        ]
        assert class_fcall_parents == [
            ("my_decorator", PyDecorator),
            ("my_decorator2", PyDecorator),
            ("d", Argument),
            ("foo", PyAssignment),
        ]


@pytest.mark.xfail(reason="Broken by function call changes")
def test_function_calls_from_datatypes(tmpdir):
    # language=python
    content = """
def get_config():
    # dictionary
    config = {
        "max_retries": get_max_retries(),
        "timeout": calculate_timeout()
    }
    return config

# tuple
data = (get_x(), get_y(), get_z())

# lambda
transformed = map(lambda x: transform(x), data)

# array
subset = my_list[start_index():end_index()]
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        fcalls = file.function_calls

        assert set(f.name for f in fcalls) == {"get_max_retries", "calculate_timeout", "get_x", "get_y", "get_z", "transform", "map", "start_index", "end_index"}
        assert len(fcalls) == 9
        fcall_parents = [(f.parent.parent.level, f.name, f.parent.statement_type) for f in fcalls]
        assert fcall_parents == [
            # dictionary
            (1, "get_max_retries", StatementType.ASSIGNMENT),
            (1, "calculate_timeout", StatementType.ASSIGNMENT),
            # tuple
            (0, "get_x", StatementType.ASSIGNMENT),
            (0, "get_y", StatementType.ASSIGNMENT),
            (0, "get_z", StatementType.ASSIGNMENT),
            # lambda
            (0, "map", StatementType.ASSIGNMENT),
            (0, "transform", StatementType.ASSIGNMENT),
            # array
            (0, "start_index", StatementType.ASSIGNMENT),
            (0, "end_index", StatementType.ASSIGNMENT),
        ]


def test_function_calls_from_function_parameters(tmpdir):
    # language=python
    content = """
# function parameters
def greet(name=get_default_name()):
    print(f"Hello, {name}!")
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        fcalls = file.function_calls
        func = file.get_function("greet")

        assert set(f.name for f in fcalls) == {"get_default_name", "print"}
        assert len(fcalls) == 2
        fcall_parents = [(f.name, f.parent) for f in file.function_calls]
        assert fcall_parents == [
            ("get_default_name", func.parameters[0]),
            ("print", func.code_block.statements[0]),
        ]


def test_function_calls_from_while_loop(tmpdir):
    # language=python
    content = """
# while loop conditions
while has_next_item():
    process_item()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        fcalls = file.function_calls

        assert set(f.name for f in fcalls) == {"has_next_item", "process_item"}
        assert len(fcalls) == 2
        fcall_parents = [(f.parent.parent.level, f.name, f.parent.statement_type) for f in file.function_calls]
        assert fcall_parents == [
            (0, "has_next_item", StatementType.WHILE_STATEMENT),
            (1, "process_item", StatementType.EXPRESSION_STATEMENT),
        ]


def test_function_calls_from_if_conditions(tmpdir):
    # language=python
    content = """
# if conditions
if is_valid(user_input):
    process_data()
elif is_invalid(user_input):
    handle_error()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        fcalls = file.function_calls

        assert set(f.name for f in fcalls) == {"is_valid", "process_data", "is_invalid", "handle_error"}
        assert len(fcalls) == 4
        fcall_parents = [(f.name, type(f.parent)) for f in file.function_calls]
        assert fcall_parents == [
            ("is_valid", PyIfBlockStatement),
            ("process_data", ExpressionStatement),
            ("is_invalid", PyIfBlockStatement),
            ("handle_error", ExpressionStatement),
        ]


def test_function_calls_from_with_clause(tmpdir):
    # language=python
    content = """
# with clause
with open('file.txt', 'r') as file:
    content = file.read()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        fcalls = file.function_calls
        with_statement = file.code_block.with_statements[0]

        assert set(f.name for f in fcalls) == {"open", "read"}
        assert len(fcalls) == 2
        fcall_parents = [(f.name, f.parent) for f in fcalls]
        assert fcall_parents == [
            ("open", with_statement.clause),
            ("read", with_statement.code_block.statements[0].assignments[0]),
        ]


@pytest.mark.skip(reason="Ellen: why is this test empty?")
def test_function_calls_from_function_calls(tmpdir):
    pass
