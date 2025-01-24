from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_decorator_simple_name(tmpdir) -> None:
    # language=python
    content = """
@measure
def foo():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_function("foo")
        assert len(foo.decorators) == 1
        measure_decorator = foo.decorators[0]
        assert measure_decorator.name == "measure"


def test_decorator_dotted_name(tmpdir) -> None:
    # language=python
    content = """
@measure.performance
def foo():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_function("foo")
        assert len(foo.decorators) == 1
        measure_decorator = foo.decorators[0]
        assert measure_decorator.full_name == "measure.performance"


def test_decorator_name_function_call(tmpdir) -> None:
    # language=python
    content = """
@measure.performance.do(a=1, b=2)
def foo():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_function("foo")
        assert len(foo.decorators) == 1
        measure_decorator = foo.decorators[0]
        assert measure_decorator.full_name == "measure.performance.do"
