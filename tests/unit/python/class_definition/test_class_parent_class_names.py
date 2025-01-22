from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.interfaces.editable import Editable


def test_class_edit_parent_class_names(tmpdir) -> None:
    # language=python
    content = """
class Cube(ThreeDimensionalShape, Shape[TColor], ABC):
    side_length: int

    def __init__(self, color: str, side_length: int):
        super().__init__(color)
        self.side_length = side_length
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        cls = file.get_class("Cube")
        parent_class_names = cls.parent_class_names

        assert all(isinstance(x, Editable) for x in parent_class_names)
        assert len(parent_class_names) == 3
        assert [x.source for x in parent_class_names] == ["ThreeDimensionalShape", "Shape", "ABC"]

        parent_class_names[0].edit("TwoDimensionalShape")
        parent_class_names[1].edit("Toy")
        parent_class_names[2].edit("XYZ")
        codebase.commit()

        cls = file.get_class("Cube")
        assert [x.source for x in cls.parent_class_names] == ["TwoDimensionalShape", "Toy", "XYZ"]
        assert "class Cube(TwoDimensionalShape, Toy[TColor], XYZ):" in file.content
