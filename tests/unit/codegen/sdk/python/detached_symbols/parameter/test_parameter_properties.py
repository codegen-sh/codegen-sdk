from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_parameter_basic_properties(tmpdir) -> None:
    # language=python
    content = """
def foo(a, b: int, c=1, d: int = 2):
    pass

def bar(*args, **kwargs):
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        function_symbol = file.get_function("foo")

        assert len(function_symbol.parameters) == 4

        # First Parameter
        assert function_symbol.parameters[0].name == "a"
        assert not function_symbol.parameters[0].is_typed
        assert not function_symbol.parameters[0].type
        assert not function_symbol.parameters[0].type
        assert function_symbol.parameters[0].default is None

        # Second Parameter
        assert function_symbol.parameters[1].name == "b"
        assert function_symbol.parameters[1].is_typed
        assert function_symbol.parameters[1].type == "int"
        assert function_symbol.parameters[1].type == "int"
        assert function_symbol.parameters[1].default is None

        # Third Parameter
        assert function_symbol.parameters[2].name == "c"
        assert not function_symbol.parameters[2].is_typed
        assert not function_symbol.parameters[2].type
        assert not function_symbol.parameters[2].type
        assert function_symbol.parameters[2].default == "1"

        # Fourth Parameter
        assert function_symbol.parameters[3].name == "d"
        assert function_symbol.parameters[3].is_typed
        assert function_symbol.parameters[3].type == "int"
        assert function_symbol.parameters[3].type == "int"
        assert function_symbol.parameters[3].default == "2"

        # TODO: *args and **kwargs are not yet supported!
        # #
        # # Function bar
        # #
        # function_symbol = codebase.get_symbol("bar")

        # assert len(function_symbol.parameters) == 2

        # # First Parameter
        # assert function_symbol.parameters[0].name == "args"
        # assert function_symbol.parameters[1].name == "kwargs"


def test_parameter_default_value(tmpdir) -> None:
    # language=python
    content = """
DEFAULT_VALUE = 3

def foo(x: int = DEFAULT_VALUE):
    return x + 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        default_val_var = file.get_global_var("DEFAULT_VALUE")
        function_symbol = file.get_function("foo")

        assert len(function_symbol.parameters) == 1
        param = function_symbol.parameters[0]

        # First Parameter
        assert param.name == "x"
        assert param.is_typed
        assert param.type == "int"
        assert param.value == "DEFAULT_VALUE"

        assert len(default_val_var.usages) == 2
        assert default_val_var.usages[0].match.parent_statement == function_symbol.code_block.statements[0]
        assert default_val_var.usages[1].match == param.value
