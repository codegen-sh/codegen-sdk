from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_global_var_dependencies_none(tmpdir) -> None:
    # language=python
    content = """
GLOBAL_VAR_1 = 234
GLOBAL_VAR_2 = 432

def foo(tmpdir):
    local_var = 123
    return local_var + GLOBAL_VAR_2
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        assert set(dep.name for dep in file.get_symbol("GLOBAL_VAR_1").dependencies) == set()
        assert set(dep.name for dep in file.get_symbol("GLOBAL_VAR_2").dependencies) == set()
