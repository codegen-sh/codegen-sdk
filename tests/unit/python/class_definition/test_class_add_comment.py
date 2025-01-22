from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_set_comment_to_method(tmpdir) -> None:
    # language=python
    content = """
class Bar:
    @old
    def bar(fun):
        return fun
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        class_symbol = file.get_class("Bar")
        bar = class_symbol.get_method("bar")
        bar.set_comment("This is a comment")
    # language=python
    assert (
        file.content
        == """
class Bar:
    # This is a comment
    @old
    def bar(fun):
        return fun
"""
    )
