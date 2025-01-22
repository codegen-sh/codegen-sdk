from codegen_sdk.codebase.factory.get_session import get_codebase_session
from codegen_sdk.python import PyFile, PyFunction


def test_function_callsites(tmpdir) -> None:
    # language=python
    content = """
def f(tmpdir):
    pass

def g(tmpdir):
    return f()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        symbol: PyFunction = file.get_function("f")
        call_sites = symbol.call_sites
        assert len(call_sites) == 1
        assert call_sites[0].name == "f"
        assert len(call_sites[0].args) == 0


def test_function_nested_callsites(tmpdir) -> None:
    # language=python
    content = """
def f(arg):
    pass

def g(tmpdir):
    f(f(None))
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file: PyFile = codebase.get_file("test.py")
        symbol = file.get_function("f")
        call_sites = symbol.call_sites
        assert len(call_sites) == 2
        assert call_sites[0].name == "f"
        assert len(call_sites[0].args) == 1


def test_function_chained_call_sites(tmpdir) -> None:
    # language=python
    content1 = """
def f():
    g().j()

def g():
    f().h()
    """
    # language=python
    content2 = """
from dir.file1 import f, g

def i():
    f().h()
    g().j().g()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")

        f = file1.get_function("f")
        g = file1.get_function("g")
        assert len(f.call_sites) == 2
        assert len(g.call_sites) == 2

        assert set([fcall.parent_symbol.name for fcall in f.call_sites]) == {"g", "i"}
        assert set([fcall.parent_symbol.name for fcall in g.call_sites]) == {"f", "i"}

        f.rename("renamed_f")
        g.rename("renamed_g")
    # language=python
    assert (
        file1.content
        == """
def renamed_f():
    renamed_g().j()

def renamed_g():
    renamed_f().h()
    """
    )
    # language=python
    assert (
        file2.content
        == """
from dir.file1 import renamed_f, renamed_g

def i():
    renamed_f().h()
    renamed_g().j().g()
    """
    )


def test_function_call_sites_excludes_methods(tmpdir) -> None:
    # language=python
    content1 = """
def f():
    g()

def g():
    f() + StaticClass.f()
    """
    # language=python
    content2 = """
from dir.file1 import f, g as h

def i():
    f() + h()
    StaticClass.f()
    StaticClass.g()

def j():
    h()
    g()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")

        f = file1.get_function("f")
        g = file1.get_function("g")
        assert len(f.call_sites) == 2
        assert len(g.call_sites) == 3

        assert set([fcall.parent_symbol.name for fcall in f.call_sites]) == {"g", "i"}
        assert set([fcall.parent_symbol.name for fcall in g.call_sites]) == {"f", "i", "j"}

        f.rename("renamed_f")
        g.rename("renamed_g")
    # language=python
    assert (
        file1.content
        == """
def renamed_f():
    renamed_g()

def renamed_g():
    renamed_f() + StaticClass.f()
    """
    )
    # language=python
    assert (
        file2.content
        == """
from dir.file1 import renamed_f, renamed_g as h

def i():
    renamed_f() + h()
    StaticClass.f()
    StaticClass.g()

def j():
    h()
    g()
    """
    )


def test_function_call_sites_indirectly_imported(tmpdir) -> None:
    # language=python
    content1 = """
def f():
    g()

def g():
    f()
    """
    # language=python
    content2 = """
from dir.file1 import f, g as h

def i():
    f() + h()
    """
    # language=python
    content3 = """
from dir.file2 import f # indirect import
from dir.file2 import h as g # aliased indirect import

def k():
    f() + f()

def l():
    my_file.g() + g()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        file3 = codebase.get_file("dir/file3.py")

        f = file1.get_function("f")
        g = file1.get_function("g")

        assert len(f.usages) == 6
        assert len(g.usages) == 5
        assert len(f.call_sites) == 4
        assert len(g.call_sites) == 3
        assert set([fcall.parent_symbol.name for fcall in f.call_sites]) == {"g", "i", "k"}
        assert set([fcall.parent_symbol.name for fcall in g.call_sites]) == {"f", "i", "l"}

        f.rename("renamed_f")
        g.rename("renamed_g")

    # language=python
    assert (
        file1.content
        == """
def renamed_f():
    renamed_g()

def renamed_g():
    renamed_f()
    """
    )
    # language=python
    assert (
        file2.content
        == """
from dir.file1 import renamed_f, renamed_g as h

def i():
    renamed_f() + h()
    """
    )
    # language=python
    assert (
        file3.content
        == """
from dir.file2 import renamed_f # indirect import
from dir.file2 import h as g # aliased indirect import

def k():
    renamed_f() + renamed_f()

def l():
    my_file.g() + g()
    """
    )


def test_function_call_sites_imported_function(tmpdir) -> None:
    # language=python
    content1 = """
def f():
    g()

def g():
    f()
    """
    # language=python
    content2 = """
from dir.file1 import f, g as h

def i():
    f() + h()
    StaticClass.f()
    StaticClass.g()

def j():
    h()
    g()
    """
    # language=python
    content3 = """
from dir import file1 as my_file
from dir.nested_dir import x

def k():
    my_file.f() + my_file.f()
    x.my_file.f()

def l():
    my_file.g()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        file3 = codebase.get_file("dir/file3.py")
        f = file1.get_function("f")
        g = file1.get_function("g")
        i = file2.get_function("i")
        j = file2.get_function("j")
        k = file3.get_function("k")
        l = file3.get_function("l")  # noqa: E741
        assert set(f.symbol_usages) == {g, i, file2.imports[0], k}
        assert len(f.usages) == 5
        assert set(g.symbol_usages) == {f, i, j, file2.imports[1], l}
        assert len(g.usages) == 5
        assert len(f.call_sites) == 4
        assert len(g.call_sites) == 4

        assert set([fcall.parent_symbol.name for fcall in f.call_sites]) == {"g", "i", "k"}
        assert set([fcall.parent_symbol.name for fcall in g.call_sites]) == {"f", "i", "j", "l"}

        f.rename("renamed_f")
        g.rename("renamed_g")
    # language=python
    assert (
        file1.content
        == """
def renamed_f():
    renamed_g()

def renamed_g():
    renamed_f()
    """
    )
    # language=python
    assert (
        file2.content
        == """
from dir.file1 import renamed_f, renamed_g as h

def i():
    renamed_f() + h()
    StaticClass.f()
    StaticClass.g()

def j():
    h()
    g()
    """
    )
    # language=python
    assert (
        file3.content
        == """
from dir import file1 as my_file
from dir.nested_dir import x

def k():
    my_file.renamed_f() + my_file.renamed_f()
    x.my_file.f()

def l():
    my_file.renamed_g()
    """
    )


def test_function_call_sites_indirect_module_import(tmpdir) -> None:
    # language=python
    content1 = """
def f():
    g()

def g():
    f()
    """
    # language=python
    content2 = """
from dir import file1

def i():
    file1.f().h()

def j():
    h()
    file1.g()
    """
    # language=python
    content3 = """
from dir.file2 import file1 as my_file

def k():
    my_file.f() + my_file.g()
    x.my_file.f()

def l():
    my_file.g().h()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        file3 = codebase.get_file("dir/file3.py")

        f = file1.get_function("f")
        g = file1.get_function("g")
        assert len(f.call_sites) == 3
        assert len(g.call_sites) == 4

        assert set([fcall.parent_symbol.name for fcall in f.call_sites]) == {"g", "i", "k"}
        assert set([fcall.parent_symbol.name for fcall in g.call_sites]) == {"f", "j", "k", "l"}

        f.rename("renamed_f")
        g.rename("renamed_g")
    # language=python
    assert (
        file1.content
        == """
def renamed_f():
    renamed_g()

def renamed_g():
    renamed_f()
    """
    )
    # language=python
    assert (
        file2.content
        == """
from dir import file1

def i():
    file1.renamed_f().h()

def j():
    h()
    file1.renamed_g()
    """
    )
    # language=python
    assert (
        file3.content
        == """
from dir.file2 import file1 as my_file

def k():
    my_file.renamed_f() + my_file.renamed_g()
    x.my_file.f()

def l():
    my_file.renamed_g().h()
    """
    )
