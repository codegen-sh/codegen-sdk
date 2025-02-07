import pprint

from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_json_basic(tmpdir, snapshot) -> None:
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
        pprint.pprint(foo_class.json())
        # TODO: make json encoding work
        # snapshot.assert_match(orjson.dumps(foo_class.json()), "test_json_basic.json")


# def test_json_stdlib(tmpdir) -> None:
#     # language=python
#     content = """
#     class Foo:
#         def foo(fun):
#             return fun
#
#     class Bar:
#         bar: int = 0
#     """
#     with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
#         file = codebase.get_file("test.py")
#
#         foo_class = file.get_class("Foo")
#         original = foo_class.json()
#         pprint(original)
#         serialized = json.dumps(original, default=to_jsonable_python)
#         assert json.loads(serialized) == original
