from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_global_var_attribute(tmpdir) -> None:
    # language=python
    content = """
A = Thing()

def foo():
    pass

A.bar = foo
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        assert len(codebase.global_vars) == 2
        foo = codebase.get_symbol("foo")
        assert len(foo.symbol_usages) == 1
        A = codebase.get_symbol("A")
        assert len(A.symbol_usages) == 1
