from codegen_sdk.codebase.factory.get_session import get_codebase_session
from codegen_sdk.codebase.flagging.enums import MessageType


def test_code_flag_properties(tmpdir):
    # language=python
    content = """
    class Foo:
        def foo(fun):
            return fun

    class Bar:
        bar: int = 0
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo_class = file.get_class("Foo")

        flag = foo_class.flag(message="test message", message_type=MessageType.GITHUB, message_recipient="12345")

    assert flag.hash
    assert flag.filepath == "test.py"
