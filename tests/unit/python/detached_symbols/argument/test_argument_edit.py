from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_argument_edit_updates_source(tmpdir) -> None:
    # language=python
    content = """
def my_function():
    my_var = do_a_thing(
        arg1=value1.id,
        arg2=value2.value,
    )
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")

        my_function = file.get_function("my_function")
        fcall = my_function.function_calls[0]
        first_arg = fcall.args[0]
        assert first_arg.source == "arg1=value1.id"
        first_arg.edit("arg3=fetch_one(MyModel, value1).content")

    assert "arg3=fetch_one(MyModel, value1).content" in file.content
