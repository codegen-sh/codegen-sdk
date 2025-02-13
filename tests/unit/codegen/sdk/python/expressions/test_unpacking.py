from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_remove_unpacking_assignment(tmpdir) -> None:
    # language=python
    content = """foo,bar,buzz = (a, b, c)"""

    with get_codebase_session(tmpdir=tmpdir, files={"test1.py": content, "test2.py": content, "test3.py": content}) as codebase:
        file1 = codebase.get_file("test1.py")
        file2 = codebase.get_file("test2.py")
        file3 = codebase.get_file("test3.py")

        foo = file1.get_symbol("foo")
        foo.remove()
        codebase.commit()

        assert len(file1.symbols) == 2
        statement = file1.symbols[0].parent
        assert len(statement.assignments) == 2
        assert len(statement.value) == 2
        assert file1.source == """bar,buzz = (b, c)"""
        bar = file2.get_symbol("bar")
        bar.remove()
        codebase.commit()
        assert len(file2.symbols) == 2
        statement = file2.symbols[0].parent
        assert len(statement.assignments) == 2
        assert len(statement.value) == 2
        assert file2.source == """foo,buzz = (a, c)"""

        buzz = file3.get_symbol("buzz")
        buzz.remove()
        codebase.commit()

        assert len(file3.symbols) == 2
        statement = file3.symbols[0].parent
        assert len(statement.assignments) == 2
        assert len(statement.value) == 2
        assert file3.source == """foo,bar = (a, b)"""

        file1_bar = file1.get_symbol("bar")

        file1_bar.remove()
        codebase.commit()
        assert file1.source == """buzz = c"""

        file1_buzz = file1.get_symbol("buzz")
        file1_buzz.remove()

        codebase.commit()
        assert len(file1.symbols) == 0
        assert file1.source == """"""


def test_remove_unpacking_assignment_funct(tmpdir) -> None:
    # language=python
    content = """foo,bar,buzz = f()"""

    with get_codebase_session(tmpdir=tmpdir, files={"test1.py": content, "test2.py": content, "test3.py": content}) as codebase:
        file1 = codebase.get_file("test1.py")
        file2 = codebase.get_file("test2.py")
        file3 = codebase.get_file("test3.py")

        foo = file1.get_symbol("foo")
        foo.remove()
        codebase.commit()

        assert len(file1.symbols) == 3
        statement = file1.symbols[0].parent
        assert len(statement.assignments) == 3
        assert file1.source == """_,bar,buzz = f()"""
        bar = file2.get_symbol("bar")
        bar.remove()
        codebase.commit()
        assert len(file2.symbols) == 3
        statement = file2.symbols[0].parent
        assert len(statement.assignments) == 3
        assert file2.source == """foo,_,buzz = f()"""

        buzz = file3.get_symbol("buzz")
        buzz.remove()
        codebase.commit()

        assert len(file3.symbols) == 3
        statement = file3.symbols[0].parent
        assert len(statement.assignments) == 3
        assert file3.source == """foo,bar,_ = f()"""

        file1_bar = file1.get_symbol("bar")
        file1_buzz = file1.get_symbol("buzz")

        file1_bar.remove()
        file1_buzz.remove()
        codebase.commit()
        assert len(file1.symbols) == 0
        assert file1.source == """"""


def test_remove_unpacking_assignment_num(tmpdir) -> None:
    # language=python
    content = """foo,bar,buzz = (1, 2, 3)"""

    with get_codebase_session(tmpdir=tmpdir, files={"test1.py": content}) as codebase:
        file1 = codebase.get_file("test1.py")

        foo = file1.get_symbol("foo")
        buzz = file1.get_symbol("buzz")

        foo.remove()
        buzz.remove()
        codebase.commit()

        assert len(file1.symbols) == 1
        statement = file1.symbols[0].parent
        assert len(statement.assignments) == 1
        assert file1.source == """bar = 2"""
