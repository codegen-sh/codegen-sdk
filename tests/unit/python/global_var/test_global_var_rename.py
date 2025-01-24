from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_global_var_rename_updates_usages_in_method(tmpdir) -> None:
    # language=python
    content1 = """
global_var = 1

class MyClass:
    def foo(self):
        return global_var
        """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1}) as codebase:
        file = codebase.get_file("file1.py")
        global_var = file.get_global_var("global_var")
        assert len(global_var.symbol_usages) == 1
        global_var.rename("new_var")

    # language=python
    assert (
        file.content
        == """
new_var = 1

class MyClass:
    def foo(self):
        return new_var
        """
    )


# TODO: CG-9317 - implement lambda functions. Currently isn't a callable but works due to a hack
def test_global_var_rename_updates_usages_in_decorators(tmpdir) -> None:
    # language=python
    content1 = """
global_var = 1
global_func = lambda: global_var

@global_func
@apidoc
class MyClass:

    @noapidoc
    @global_func.setter
    def foo(self):
        global_func()
        return global_var
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1}) as codebase:
        file = codebase.get_file("file1.py")
        global_var = file.get_global_var("global_var")
        global_func = file.get_global_var("global_func")

        global_var.rename("new_global_var")
        global_func.rename("new_global_func")

    # language=python
    assert (
        file.content
        == """
new_global_var = 1
new_global_func = lambda: new_global_var

@new_global_func
@apidoc
class MyClass:

    @noapidoc
    @new_global_func.setter
    def foo(self):
        new_global_func()
        return new_global_var
    """
    )
