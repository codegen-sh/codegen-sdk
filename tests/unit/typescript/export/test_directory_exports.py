from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.enums import ProgrammingLanguage


def test_directory_exports(tmpdir) -> None:
    # language=typescript
    content1 = """
    export const a = 1;
    export const b = 2;
    """
    content2 = """
    export const c = 3;
    export const d = 4;
    """
    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "dir1/file1.ts": content1,
            "dir1/file2.ts": content2,
            "dir2/file3.ts": "export const e = 5;"
        },
        programming_language=ProgrammingLanguage.TYPESCRIPT
    ) as codebase:
        dir1 = codebase.get_directory("dir1")
        dir2 = codebase.get_directory("dir2")
        
        # Test dir1 exports
        assert len(dir1.exports) == 4
        dir1_export_names = {exp.name for exp in dir1.exports}
        assert dir1_export_names == {"a", "b", "c", "d"}
        
        # Test dir2 exports
        assert len(dir2.exports) == 1
        assert dir2.exports[0].name == "e"
        
        # Test get_export method
        assert dir1.get_export("a") is not None
        assert dir1.get_export("e") is None
        assert dir2.get_export("e") is not None