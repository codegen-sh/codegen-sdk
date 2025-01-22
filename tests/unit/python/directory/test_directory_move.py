from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_directory_file_move_simple(tmpdir) -> None:
    # language=python
    content1 = """
def a():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir_a/file1.py": content1}) as codebase:
        assert {d.dirpath for d in codebase.directories} == {"", "dir_a"}
        assert codebase.get_directory("dir_a", optional=True) is not None
        assert codebase.get_file("dir_a/file1.py", optional=True) is not None
        codebase.get_file("dir_a/file1.py").update_filepath("dir_b/file1.py")
        codebase.commit()
        assert {d.dirpath for d in codebase.directories} == {"", "dir_b"}
        assert codebase.get_file("dir_b/file1.py", optional=True) is not None
        assert codebase.get_file("dir_a/file1.py", optional=True) is None
        assert codebase.get_directory("dir_a", optional=True) is None
        assert codebase.get_directory("dir_b", optional=True) is not None


def test_directory_file_move_subdir(tmpdir) -> None:
    # language=python
    content1 = """
def a():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/subdir_a/file1.py": content1}) as codebase:
        assert {d.dirpath for d in codebase.directories} == {"", "dir", "dir/subdir_a"}
        assert codebase.get_directory("dir", optional=True) is not None
        assert codebase.get_directory("dir/subdir_a", optional=True) is not None
        assert codebase.get_file("dir/subdir_a/file1.py", optional=True) is not None
        codebase.get_file("dir/subdir_a/file1.py").update_filepath("dir/subdir_b/file1.py")
        codebase.commit()
        assert {d.dirpath for d in codebase.directories} == {"", "dir", "dir/subdir_b"}
        assert codebase.get_directory("dir", optional=True) is not None
        assert codebase.get_file("dir/subdir_b/file1.py", optional=True) is not None
        assert codebase.get_file("dir/subdir_a/file1.py", optional=True) is None
        assert codebase.get_directory("dir/subdir_a", optional=True) is None
        assert codebase.get_directory("dir/subdir_b", optional=True) is not None


def test_directory_file_move_into_subdir(tmpdir) -> None:
    # language=python
    content1 = """
def a():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1}) as codebase:
        assert {d.dirpath for d in codebase.directories} == {"", "dir"}
        assert codebase.get_directory("dir", optional=True) is not None
        assert codebase.get_directory("dir/subdir", optional=True) is None
        assert codebase.get_file("dir/file1.py", optional=True) is not None
        codebase.get_file("dir/file1.py").update_filepath("dir/subdir/file1.py")
        codebase.commit()
        assert {d.dirpath for d in codebase.directories} == {"", "dir", "dir/subdir"}
        assert codebase.get_directory("dir", optional=True) is not None
        assert codebase.get_directory("dir/subdir", optional=True) is not None
        assert codebase.get_file("dir/subdir/file1.py", optional=True) is not None
        assert codebase.get_file("dir/file1.py", optional=True) is None


def test_directory_file_move_out_of_subdir(tmpdir) -> None:
    # language=python
    content1 = """
def a():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/subdir/file1.py": content1}) as codebase:
        assert {d.dirpath for d in codebase.directories} == {"", "dir", "dir/subdir"}
        assert codebase.get_directory("dir", optional=True) is not None
        assert codebase.get_directory("dir/subdir", optional=True) is not None
        assert codebase.get_file("dir/subdir/file1.py", optional=True) is not None
        codebase.get_file("dir/subdir/file1.py").update_filepath("dir/file1.py")
        codebase.commit()
        assert {d.dirpath for d in codebase.directories} == {"", "dir"}
        assert codebase.get_directory("dir", optional=True) is not None
        assert codebase.get_directory("dir/subdir", optional=True) is None
        assert codebase.get_file("dir/file1.py", optional=True) is not None
        assert codebase.get_file("dir/subdir/file1.py", optional=True) is None


def test_directory_move(tmpdir) -> None:
    # language=python
    content1 = """
def a():
    pass
    """
    # language=python
    content2 = """
def b():
    pass
    """
    # language=python
    content3 = """
def c():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir_a/file1.py": content1, "dir_a/file2.py": content2, "dir_a/subdir/file3.py": content3}) as codebase:
        assert {d.dirpath for d in codebase.directories} == {"", "dir_a", "dir_a/subdir"}
        assert codebase.get_directory("dir_a", optional=True) is not None
        assert codebase.get_directory("dir_b", optional=True) is None
        codebase.get_directory("dir_a").update_filepath("dir_b")
        codebase.commit()
        assert {d.dirpath for d in codebase.directories} == {"", "dir_b", "dir_b/subdir"}
        assert codebase.get_directory("dir_b", optional=True) is not None
        assert codebase.get_directory("dir_a", optional=True) is None
        assert codebase.get_file("dir_b/file1.py", optional=True) is not None
        assert codebase.get_file("dir_b/file2.py", optional=True) is not None
        assert codebase.get_file("dir_b/subdir/file3.py", optional=True) is not None
        assert codebase.get_file("dir_a/file1.py", optional=True) is None
        assert codebase.get_file("dir_a/file2.py", optional=True) is None
        assert codebase.get_file("dir_a/subdir/file3.py", optional=True) is None


def test_directory_rename(tmpdir) -> None:
    # language=python
    content1 = """
def a():
    pass
    """
    # language=python
    content2 = """
def b():
    pass
    """
    # language=python
    content3 = """
def c():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/subdir/file3.py": content3}) as codebase:
        assert {d.dirpath for d in codebase.directories} == {"", "dir", "dir/subdir"}
        assert codebase.get_directory("dir", optional=True) is not None
        codebase.get_directory("dir").rename("dir_new")
        codebase.commit()
        assert {d.dirpath for d in codebase.directories} == {"", "dir_new", "dir_new/subdir"}
        assert codebase.get_directory("dir_new", optional=True) is not None
        assert codebase.get_directory("dir", optional=True) is None
        assert codebase.get_file("dir_new/file1.py", optional=True) is not None
        assert codebase.get_file("dir_new/file2.py", optional=True) is not None
        assert codebase.get_file("dir_new/subdir/file3.py", optional=True) is not None
        assert codebase.get_file("dir/file1.py", optional=True) is None
        assert codebase.get_file("dir/file2.py", optional=True) is None
        assert codebase.get_file("dir/subdir/file3.py", optional=True) is None
