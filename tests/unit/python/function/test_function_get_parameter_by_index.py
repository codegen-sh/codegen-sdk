from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_function_get_parameter_by_index(tmpdir) -> None:
    # language=python
    file = """
def foo(a: int, b: str):
    print(a)
    print(b)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": file}) as codebase:
        file = codebase.get_file("file.py")
        symbol = file.get_function("foo")
        parameter = symbol.get_parameter_by_index(0)

    assert parameter.name == "a"
