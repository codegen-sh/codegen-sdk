from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_class_inherited_method_parent_detection(tmpdir) -> None:
    # language=python
    content = """
class Parent:
    def parent_method(self):
        return "from parent"

    def overridden_method(self):
        return "parent version"

class Child(Parent):
    def child_method(self):
        return "from child"

    def overridden_method(self):
        return "child version"
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        child = file.get_class("Child")
        parent = file.get_class("Parent")

        # Track which methods we found
        found_methods = {"parent_method": False, "child_method": False, "overridden_method": False}

        # Check each method's parent class
        for method in child.methods(max_depth=None):
            if method.name == "parent_method":
                assert method.parent_class == parent
                found_methods["parent_method"] = True
            elif method.name == "child_method":
                assert method.parent_class == child
                found_methods["child_method"] = True
            elif method.name == "overridden_method":
                assert method.parent_class == child  # Should get the overridden version
                found_methods["overridden_method"] = True

        # Verify we found all methods
        assert all(found_methods.values()), "Not all methods were found"
