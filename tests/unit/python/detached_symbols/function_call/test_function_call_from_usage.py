from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.detached_symbols.function_call import FunctionCall


def test_function_call_from_usage(tmpdir) -> None:
    # language=python
    content = """
def test_function():
    user1 = UserFactory.create()
    user2 = UserFactory.create()
    user3 = UserFactory.create()

    # Different ways of calling factory with user_id
    SomeFactory(user_id=user1.id)
    SomeFactory.create(user_id=user2.id)
    SomeFactory.build(user_id=user3.id)
    SomeFactory.other_method(user_id=user3.id)
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        usages = file.find("SomeFactory.create", exact=True)
        usages += file.find("SomeFactory.build", exact=True)
        usages += file.search(r"\bSomeFactory\(")
        for usage in usages:
            function_call = FunctionCall.from_usage(usage)
            user_arg = function_call.get_arg_by_parameter_name("user_id")
            if user_arg:
                arg_value = user_arg.value.source

                # Replace the arg value with the correct value
                if arg_value.endswith(".id"):
                    user_arg.set_value(arg_value.replace(".id", ""))
                else:
                    continue

                # Update the arg keyword
                user_arg.rename("user")

    # language=python
    assert (
        file.content
        == """
def test_function():
    user1 = UserFactory.create()
    user2 = UserFactory.create()
    user3 = UserFactory.create()

    # Different ways of calling factory with user_id
    SomeFactory(user=user1)
    SomeFactory.create(user=user2)
    SomeFactory.build(user=user3)
    SomeFactory.other_method(user_id=user3.id)
    """
    )
