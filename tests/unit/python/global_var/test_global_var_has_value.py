from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_global_var_single_var(tmpdir) -> None:
    # language=python
    content = """
a = 1
b = "string"
c = 1.0
d = [1, 2, 3]
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.global_vars) == 4
        a = file.get_global_var("a")
        b = file.get_global_var("b")
        c = file.get_global_var("c")
        d = file.get_global_var("d")

        assert a.value == "1"
        assert b.value == '"string"'
        assert c.value == "1.0"
        assert d.value == "[1, 2, 3]"
        a.set_value("2")
        b.set_value('"new string"')
        c.set_value("2.0")
        d.set_value("[2, 3, 4]")

    assert file.get_global_var("a").value == "2"
    assert file.get_global_var("b").value == '"new string"'
    assert file.get_global_var("c").value == "2.0"
    assert file.get_global_var("d").value == "[2, 3, 4]"


def test_global_var_pattern_list(tmpdir) -> None:
    content = "first, *rest = [1, 2, 3, 4, 5]"
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.global_vars) == 2
        first = file.get_global_var("first")
        rest = file.get_global_var("rest")

        assert first.value == "[1, 2, 3, 4, 5]"
        assert rest.value == "[1, 2, 3, 4, 5]"
        first.set_value("[3, 4, 5]")

    assert file.get_global_var("first").value == "[3, 4, 5]"
    assert file.get_global_var("rest").value == "[3, 4, 5]"


def test_global_var_multiple_vars(tmpdir) -> None:
    content = "x = y = z = 1"
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.global_vars) == 3
        x = file.get_global_var("x")
        y = file.get_global_var("y")
        z = file.get_global_var("z")

        assert x.value == "y = z = 1"
        assert y.value == "z = 1"
        assert z.value == "1"
        y.set_value("xyz = 2")

    assert len(file.global_vars) == 3
    assert file.get_global_var("x").value == "y = xyz = 2"
    assert file.get_global_var("y").value == "xyz = 2"
    assert file.get_global_var("xyz").value == "2"


def test_global_var_no_value(tmpdir) -> None:
    content = "a: int"
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.global_vars) == 1
        a = file.get_global_var("a")

        assert a.value is None
        a.set_value("1")

    assert file.get_global_var("a").value == "1"
    assert file.content == "a: int = 1"
