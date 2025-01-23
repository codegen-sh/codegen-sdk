import re

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from tests.unit.python.utils.test_file_contents import file1_content, file2_content


def test_function_parameter_edit(tmpdir) -> None:
    # language=python
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": file1_content, "file2.py": file2_content}) as codebase:
        file1 = codebase.get_file("file1.py")

        top_level_function = file1.get_function("top_level_function1")
        assert (
            top_level_function.source
            == """def top_level_function1(x, y, z):
    return np.square(x) + y + z + GLOBAL_CONSTANT_1"""
        )

        first_param = top_level_function.get_parameter("y")
        new_func_source = re.sub(rf"\b{first_param.source}\b", "foo", top_level_function.source)
        top_level_function.edit(new_func_source)

    top_level_function = file1.get_function("top_level_function1")
    # language=python
    assert (
        top_level_function.source
        == """def top_level_function1(x, foo, z):
    return np.square(x) + foo + z + GLOBAL_CONSTANT_1"""
    )


def test_parameter_type_edit(tmpdir) -> None:
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": file1_content, "file2.py": file2_content}) as codebase:
        file1 = codebase.get_file("file1.py")

        top_level_function = file1.get_function("top_level_function1")
        first_param = top_level_function.parameters[0]
        second_param = top_level_function.parameters[1]
        assert "def top_level_function1(x, y, z):" in top_level_function.source
        assert not first_param.is_typed
        assert not second_param.is_typed

        second_param.edit(f"{second_param.source}: int")
        first_param.edit(f"{first_param.source}: int")

    top_level_function = file1.get_function("top_level_function1")
    assert "def top_level_function1(x: int, y: int, z):" in top_level_function.source
    assert top_level_function.get_parameter("x").is_typed
    assert top_level_function.get_parameter("y").is_typed
