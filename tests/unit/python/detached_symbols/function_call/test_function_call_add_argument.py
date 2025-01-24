from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.function import Function


def test_function_call_insert_argument(tmpdir) -> None:
    # language=python
    content = """
def func_1(a: int, b: int) -> int:
    func_2(a, b)

def func_3(a: int, b: int) -> int:
    func_1(a=a, b=b)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        test_file = codebase.get_file("file.py")

        # =====[ Simple case ]=====
        func_1: Function = test_file.get_function("func_1")
        func_2_call = func_1.function_calls[0]
        func_2_call.args.append("c=3")
        codebase.commit()
        assert "func_2(a, b, c=3)" in test_file.content

        # =====[ Add in idx ]=====
        func_3: Function = test_file.get_function("func_3")
        func_1_call = func_3.function_calls[0]
        func_1_call.args.insert(0, "c=3")
        codebase.commit()
        assert "func_1(c=3, a=a, b=b)" in test_file.content


def test_function_call_insert_multiple_arguments(tmpdir) -> None:
    # language=python
    content = """
    def func_2(a: int, b: int, c: int | None = None) -> int:
        return a + b

    def func_1(a: int, b: int) -> int:
        func_2(a, b)

    def func_3(a: int, b: int) -> int:
        func_1(a=a, b=b)
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        test_file = codebase.get_file("file.py")

        # =====[ Add multiple args ]=====
        test_func_1: Function = test_file.get_function("func_1")
        test_func_1_call = test_func_1.function_calls[0]
        test_func_1_call.args.append("c=3")
        test_func_1_call.args.append("d=4")
        test_func_1_call.args.append("e=5")
        codebase.commit()
        assert "func_2(a, b, c=3, d=4, e=5)" in test_file.content

        # =====[ Add multiple args using idx ]=====
        func_3: Function = test_file.get_function("func_3")
        fcall = func_3.function_calls[0]
        fcall.args.insert(0, "c=3")
        fcall.args.insert(1, "d=4")
        fcall.args.insert(3, "e=5")
        fcall.args.append("f=6")
        codebase.commit()
        assert "func_1(c=3, d=4, a=a, e=5, b=b, f=6)" in test_file.content


def test_function_call_no_args_insert_argument(tmpdir) -> None:
    # language=python
    content = """
def foo():
    func_1()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        test_file = codebase.get_file("file.py")
        foo = test_file.get_function("foo")
        fcall = foo.function_calls[0]
        fcall.args.append("a=1")
        codebase.commit()

        assert "func_1(a=1)" in test_file.content


def test_function_call_no_args_insert_multiple_no_args(tmpdir) -> None:
    # language=python
    content = """
def foo():
    func_1()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        test_file = codebase.get_file("file.py")
        foo = test_file.get_function("foo")
        fcall = foo.function_calls[0]
        fcall.args.append("a=1")
        fcall.args.append("b=2")
        fcall.args.append("c=3")
        codebase.commit()
        assert "func_1(a=1, b=2, c=3)" in test_file.content


def test_function_call_no_args_insert_multiple_no_args_unordered(tmpdir) -> None:
    # language=python
    content = """
def foo():
    func_1()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_function("foo")
        func_1_call = foo.function_calls[0]
        func_1_call.args.insert(1, "b=2")
        func_1_call.args.insert(3, "a=1")
        func_1_call.args.insert(2, "c=3")
        func_1_call.args.insert(0, "d=4")
        codebase.commit()

        assert "func_1(d=4, b=2, c=3, a=1)" in file.content


def test_function_call_remove_then_insert(tmpdir) -> None:
    # language=python
    content = """
def foo():
    func_1(a=1, b=2)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_function("foo")
        fcall = foo.function_calls[0]

        # Test remove and insert
        fcall.args[-1].remove()
        fcall.args.append("c=3")
        fcall.args.append("d=4")
        codebase.commit()
        assert "func_1(a=1, c=3, d=4)" in file.content
        codebase.reset()

        # Test remove all and insert
        # for arg in fcall.args:
        #     arg.remove()
        # fcall.args.append("c=3")
        # fcall.args.append("d=4")
        # codebase.commit()
        # assert "func_1(c=3, d=4)" in file.content


def test_function_call_insert_then_remove(tmpdir) -> None:
    # language=python
    content = """
def foo():
    func_1(a=1, b=2)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_function("foo")
        fcall = foo.function_calls[0]

        # Test insert and remove
        fcall.args.append("c=3")
        fcall.args.append("d=4")
        fcall.args[-1].remove()
        codebase.commit()
        assert "func_1(a=1, c=3, d=4)" in file.content
        codebase.reset()

        # Test insert and remove all
        # fcall.args.append("c=3")
        # fcall.args.append("d=4")
        # foo = file.get_function("foo")
        # fcall = foo.function_calls[0]
        # for arg in fcall.args:
        #     arg.remove()
        # codebase.commit()
        # assert "func_1(c=3, d=4)" in file.content
