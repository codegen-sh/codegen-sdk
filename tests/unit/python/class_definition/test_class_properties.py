import pytest

from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.python import PyClass


def test_classes(tmpdir) -> None:
    # language=python
    content = """
class A:
    pass

class B:
    pass

class C:
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        # ======[ Grab the nodes ]=====
        assert file.symbols == file.classes
        symbols = file.classes
        names = [x.name for x in symbols]
        assert "A" in names
        assert "B" in names
        assert "C" in names


def test_class_methods(tmpdir) -> None:
    # language=python
    content = """
from a.b import (c as d, e as f)

@d.test("abc")
class A:
    def __init__(self):
        pass

    @property
    def method(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        cls = file.get_class("A")
        methods = cls.methods
        assert len(methods) == 2
        assert "method" in [x.name for x in cls.methods]
        assert "__init__" in [x.name for x in cls.methods]
        m = cls.get_method("method")
        assert "@property" in m.source


def test_class_decorated_definition(tmpdir) -> None:
    # language=python
    content = """
@dataclass
class MyClass:
    a: int
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("MyClass")
        assert symbol.name == "MyClass"
        assert "@dataclass" in symbol.source


def test_basic_subclasses(tmpdir) -> None:
    # language=python
    content = """
import marshmallow as ma
import subtype as SubType

class MyClass(ma.Schema, ParentClass[SubType]):
    def __init__(self, x, y, z):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        cls = file.get_class("MyClass")
        assert "ma.Schema" in [c.source for c in cls.parent_class_names]
        assert "ParentClass" in [c.source for c in cls.parent_class_names]

        assert cls.is_subclass
        assert cls.is_subclass_of("ma.Schema")
        assert cls.is_subclass_of("Schema")


def test_advanced_subclasses(tmpdir) -> None:
    # language=python
    content = """
from abc import ABC
class BaseClass(ABC):
    pass
class MyClass(BaseClass):
    def __init__(self, x, y, z):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        cls = file.get_class("MyClass")
        assert cls.is_subclass
        assert cls.is_subclass_of("abc.ABC")
        assert cls.is_subclass_of("ABC")


def test_class_get_attribute(tmpdir) -> None:
    # language=python
    content = """
class A:
    a: int = 1
    b: str = "hello"
    c = 5
    d: int
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        cls: PyClass = file.get_class("A")
        attrs = cls.attributes
        assert len(attrs) == 4
        assert "a" in [x.name for x in attrs]
        assert "b" in [x.name for x in attrs]
        assert "c" in [x.name for x in attrs]
        assert "d" in [x.name for x in attrs]
        d = cls.get_attribute("d")
        assert d is not None


def test_class_method_level(tmpdir) -> None:
    # language=python
    content = """
z = 1

class A:
    def g(tmpdir):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        A = file.get_class("A")
        g = A.get_method("g")
        assert A.code_block.level == 1
        assert g.code_block.level == 2


def test_class_docstring(tmpdir) -> None:
    # language=python
    content = """
@my_decorator1
@my_decorator2
class MyClass:
    '''
    Docstring line 1
    Docstring line 2
    '''
    def __init__(self):
        pass

    def my_method(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        my_class = file.get_class("MyClass")
        assert len(my_class.docstring.symbols) == 1
        assert "Docstring line 1" in my_class.docstring.symbols[0].source
        assert "Docstring line 2" in my_class.docstring.symbols[0].source
        assert my_class.docstring.text == "Docstring line 1\nDocstring line 2"


def test_class_method_docstring(tmpdir) -> None:
    # language=python
    content = """
class MyClass:
    @my_decorator1
    @my_decorator2
    def __init__(self):
        pass

    def my_method(self):
        '''
        Docstring line 3
        Docstring line 4
        '''
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        my_class = file.get_class("MyClass")
        init = my_class.get_method("__init__")
        my_method = my_class.get_method("my_method")
        assert init.docstring is None
        assert init.is_decorated

        assert len(my_method.docstring.symbols) == 1
        assert my_method.docstring.text == "Docstring line 3\nDocstring line 4"
        assert not my_method.is_decorated


# ED_TODO: Fixable. Needs logic bypass for comments
@pytest.mark.skip(reason="TODO: the bottom comment is not being captured (CG-8539)")
def test_class_comments(tmpdir) -> None:
    # language=python
    content = """
# This is a comment above decorators
@my_decorator1
@my_decorator2
# This is a comment below decorators
class MyClass:
    def __init__(self):
        pass

    def my_method(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        my_class = file.get_class("MyClass")

        assert len(my_class.comment.symbols) == 2
        assert my_class.comment.source == "# This is a comment above decorators\n# This is a comment below decorators"


def test_class_decorators(tmpdir) -> None:
    # language=python
    content = """
from a.b import (c as d, e as f)

def regular_func(tmpdir):
    pass

@regular_func
@d.test("abc")
@f.test("abc")
class A:

    @d.second_test("abc")
    def myfunc(self):
        f.test("abc")

    def undecorated(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        # =====[ Class decorators ]=====
        cls = file.get_class("A")
        decorators = cls.decorators
        assert cls.is_decorated
        assert len(decorators) == 3
        assert "@regular_func" in [x.source for x in decorators]
        assert '@d.test("abc")' in [x.source for x in decorators]
        assert '@f.test("abc")' in [x.source for x in decorators]

        # =====[ Method decorators ]=====
        method = cls.get_method("myfunc")
        assert method.is_decorated
        decorators = method.decorators
        assert len(decorators) == 1
        assert '@d.second_test("abc")' in [x.source for x in decorators]
        method2 = cls.get_method("undecorated")
        assert not method2.is_decorated
        assert len(method2.decorators) == 0


def test_class_comment(tmpdir) -> None:
    FILENAME = "test_file.py"
    # language=python
    FILE_CONTENT = """
# This is a comment
class Foo:
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: FILE_CONTENT.strip()}) as codebase:
        file = codebase.get_file(FILENAME)
        foo = file.get_class("Foo")

        assert foo.comment.source == "# This is a comment"
        assert "# This is a comment" in foo.extended_source
        # assert "# This is a comment" not in foo.source
        assert "class Foo:" in foo.source
        assert "class Foo:" in foo.extended_source


def test_decorated_class_extended_source(tmpdir) -> None:
    FILENAME = "test_file.py"
    # language=python
    FILE_CONTENT = """
# This is a comment
@decorator
class Foo:
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: FILE_CONTENT.strip()}) as codebase:
        file = codebase.get_file(FILENAME)
        foo = file.get_class("Foo")

        assert foo.comment.source == "# This is a comment"
        assert "# This is a comment" in foo.extended_source
        # assert "# This is a comment" not in foo.source
        assert "@decorator" in foo.extended_source
        # assert "@decorator" not in foo.source
        assert "class Foo:" in foo.source
        assert "class Foo:" in foo.extended_source
