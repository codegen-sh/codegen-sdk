from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_decorated_class_source(tmpdir) -> None:
    # language=python
    content = """
@f.test("abc")
class A:
    pass
"""
    # language=python
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        A = file.get_class("A")
        assert (
            A.source
            == """
@f.test("abc")
class A:
    pass
""".strip()
        )


def test_class_and_method_find(tmpdir) -> None:
    # language=python
    content = """
class MyClass1:
    def foo(self):
        abc = "abc"
        b = "123"

    def bar(self):
        cba = "cba"
        d = "321"
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")

        my_class = codebase.get_symbol("MyClass1")
        matches = my_class.find(["b"])
        assert len(matches) == 6
        assert set([m.source for m in matches]) == {"abc", "b", "bar", "cba"}

        foo = my_class.get_method("foo")
        matches = foo.find(["b"])
        assert len(matches) == 3
        assert set([m.source for m in matches]) == {"abc", "b"}
        matches = foo.find("b")
        assert len(matches) == 3
        assert set([m.source for m in matches]) == {"abc", "b"}


def test_class_and_method_search(tmpdir) -> None:
    # language=python
    content = """
class MyClass1:
    def foo(self):
        abc = "abc"
        b = "123"

    def bar(self):
        cba = "cba"
        d = "321"

    def hello(self):
        print("hellooo!")

    def world(self):
        print("world!")
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        five_char_pattern = r"\b\w{5}\b"

        my_class = codebase.get_symbol("MyClass1")
        matches = my_class.search(five_char_pattern)
        assert len(matches) == 6
        assert set([m.source for m in matches]) == {"class", "hello", "print", "world", "world!"}

        world = my_class.get_method("world")
        matches = world.search(five_char_pattern)
        assert len(matches) == 3
        assert set([m.source for m in matches]) == {"print", "world", "world!"}


def test_class_method_replace(tmpdir) -> None:
    # language=python
    content = """
class MyClass1:
    def foo(self):
        abc = "abc"
        b = "123"

    def bar(self):
        cba = "cba"
        d = "321"
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        my_class = codebase.get_symbol("MyClass1")
        foo = my_class.get_method("foo")
        foo.replace("foo", "foos_ball")

    assert "def foos_ball(self):" in foo.file.content
