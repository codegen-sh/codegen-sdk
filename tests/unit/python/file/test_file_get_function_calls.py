from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_file_get_function_calls(tmpdir) -> None:
    # language=python
    content = """
def get_logger(name: str) -> Logger:
    return Logger(name)

error_logger = get_logger(__name__).error()

class MyClass:
    def __init__(self):
        nested_function_call().chained().calls()

def top_level_function():
    bar()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        function_calls = file.function_calls
        assert len(function_calls) == 7
        assert set([fcall.name for fcall in function_calls]) == {"Logger", "get_logger", "error", "nested_function_call", "chained", "calls", "bar"}

        my_class = codebase.get_symbol("MyClass")
        class_fcalls = my_class.function_calls
        assert len(class_fcalls) == 3
        assert set([fcall.name for fcall in class_fcalls]) == {"nested_function_call", "chained", "calls"}

        top_level = codebase.get_symbol("top_level_function")
        function_fcalls = top_level.function_calls
        assert len(function_fcalls) == 1
        assert set([fcall.name for fcall in function_fcalls]) == {"bar"}
