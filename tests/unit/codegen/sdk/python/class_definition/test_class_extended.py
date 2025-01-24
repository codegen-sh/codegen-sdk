from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_class_extended_nodes(tmpdir) -> None:
    # language=python
    content = """
@my_decorator1
@my_decorator2
class MyClass:
    '''
    Docstring line 1
    Docstring line 2
    '''
    def __init__(self):
        pass

    def my_method(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        my_class = file.get_class("MyClass")
        assert len(my_class.extended_nodes) == 1
        assert my_class.extended_nodes[0].ts_node.type == "decorated_definition"
        assert my_class.extended_source == content.strip()
