from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_global_function_calls(tmpdir) -> None:
    # language=python
    content = """
def foo():
    pass

def bar():
    foo()

foo()

if True:
    foo()
else:
    foo()

[foo() for _ in range(10)]
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_symbol("foo")
        assert len(foo.call_sites) == 5
