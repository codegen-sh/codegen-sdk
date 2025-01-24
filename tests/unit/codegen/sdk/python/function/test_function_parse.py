# TODO: break-up this file into one for each API

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.file import SourceFile


def test_local_import(tmpdir) -> None:
    # language=python
    content = """
def f(tmpdir):
    from a.b.c import d
    import e.f.g
    d()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        imports = file.imports
        assert len(imports) == 2

        imp = file.get_import("d")
        assert imp.module.source == "a.b.c"
        assert imp.name == "d"
        assert imp.alias.source == "d"

        imp = file.get_import("e.f.g")
        assert imp.module.source == "e.f.g"
        assert imp.name == "e.f.g"
        assert imp.alias.source == "e.f.g"


def test_overload(tmpdir) -> None:
    """Test overloaded functions are not ignored"""
    # language=python
    content = """
@overload
def f(tmpdir):
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        assert len(file.functions) == 1


def test_class_overload(tmpdir) -> None:
    """Test overloaded methods are ignored"""
    # language=python
    content = """
class A:
    @overload
    def f(tmpdir):
        pass
    def f(tmpdir):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        A = codebase.get_symbol("A")
        assert len(A.methods) == 1


def test_get_function_usages_with_file_import(tmpdir) -> None:
    """Tests function.usages returns usages from file imports"""
    src_filename = "a/b/c/src.py"
    # language=python
    src_file_content = """
def update():
    pass
"""
    consumer_filename = "consumer.py"
    # language=python
    consumer_file_content = """
from a.b.c import src as operations

def func_1():
    operations.update()
"""
    with get_codebase_session(
        tmpdir=tmpdir,
        files={src_filename: src_file_content, consumer_filename: consumer_file_content},
    ) as codebase:
        src_file: SourceFile = codebase.get_file(src_filename)
        consumer_file = codebase.get_file(consumer_filename)
        src_function = src_file.get_symbol("update")
        func_1 = consumer_file.get_function("func_1")
        assert set(src_function.symbol_usages) == {func_1}
        assert set(src_function.symbol_usages) == {func_1}
        assert len(src_function.symbol_usages) == 1
        assert len(src_function.symbol_usages) == 1


def test_get_function_usages_with_file_import_through_import_usages(tmpdir) -> None:
    """This is a test that shows how you can get around the issue of not being able to access the usages attribute of a function by getting the usage from the import."""
    src_filename = "a/b/c/src.py"
    # language=python
    src_file_content = """
def update():
    pass
"""
    consumer_filename = "consumer.py"
    # language=python
    consumer_file_content = """
from a.b.c import src as operations

def func_1():
    operations.update()
"""
    with get_codebase_session(
        tmpdir=tmpdir,
        files={src_filename: src_file_content, consumer_filename: consumer_file_content},
    ) as codebase:
        src_file: SourceFile = codebase.get_file(src_filename)
        src_file_importers = src_file.importers
        usages = []
        for importer in src_file_importers:
            import_name = importer.name
            importer_usages = importer.symbol_usages
            for usage in importer_usages:
                for fcall in usage.function_calls:
                    if fcall.full_name == f"{import_name}.update":
                        usages.append(fcall)
        assert len(usages) == 1
