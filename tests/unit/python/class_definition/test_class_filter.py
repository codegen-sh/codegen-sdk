from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_class_definition_filter(tmpdir) -> None:
    # language=python
    content = """
class Foo:
    a: int
    _b: int
    def __init__(self):
        pass
    def __contains__(self, item):
        pass
    def _private(self):
        pass
    def foo(fun):
        return fun
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        foo_class = file.get_class("Foo")
        assert len(foo_class.methods(magic=False, private=False)) == 1
        assert len(foo_class.methods(magic=False, private=True)) == 2
        assert len(foo_class.methods(magic=True, private=False)) == 3
        assert len(foo_class.methods(magic=True, private=True)) == 4
        assert len(foo_class.attributes(private=True)) == 2
        assert len(foo_class.attributes(private=False)) == 1
