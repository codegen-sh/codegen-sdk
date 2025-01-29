import pytest

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.file import SourceFile


def test_codebase_edit_mdx(tmpdir) -> None:
    """Test editing MDX file content"""
    with get_codebase_session(tmpdir=tmpdir, files={"file1.mdx": "# Header", "file2.tsx": "console.log('hello, world!')"}) as codebase:
        file = codebase.get_file("file1.mdx")
        file.edit("NEW TEXT")
        codebase.commit()
        file = codebase.get_file("file1.mdx")
        assert file.content == "NEW TEXT"


def test_edit_json_file(tmpdir) -> None:
    """Test editing JSON file content"""
    with get_codebase_session(tmpdir=tmpdir, files={"config.json": '{"key": "value", "nested": {"foo": "bar"}}'}) as codebase:
        file = codebase.get_file("config.json")

        # Test complete content replacement
        file.edit('{"newKey": "newValue"}')
        codebase.commit()
        assert file.content == '{"newKey": "newValue"}'

        # Test partial content replacement
        file.edit('{"newKey": "newValue", "extra": true}')
        codebase.commit()
        assert file.content == '{"newKey": "newValue", "extra": true}'


def test_edit_txt_file(tmpdir) -> None:
    """Test editing plain text file content"""
    with get_codebase_session(tmpdir=tmpdir, files={"data.txt": "Hello\nWorld\nTest"}) as codebase:
        file = codebase.get_file("data.txt")

        # Test single line replacement
        file.edit("New World")
        codebase.commit()
        assert file.content == "New World"

        # Test multiline content
        file.edit("Line 1\nLine 2\nLine 3")
        codebase.commit()
        assert file.content == "Line 1\nLine 2\nLine 3"


def test_codebase_replace_mdx(tmpdir) -> None:
    """Test replacing content in MDX file"""
    with get_codebase_session(tmpdir=tmpdir, files={"file1.mdx": "# Header"}) as codebase:
        file = codebase.get_file("file1.mdx")
        file.replace("# Header", "NEW TEXT")
        codebase.commit()
        file = codebase.get_file("file1.mdx")
        assert file.content == "NEW TEXT"


def test_replace_non_source_file(tmpdir) -> None:
    """Test replace functionality in non-source files"""
    with get_codebase_session(tmpdir=tmpdir, files={"doc.mdx": "# Header\nThis is a test\nMore content", "config.json": '{"test": "value", "other": "test"}'}) as codebase:
        # Test single replacement
        mdx_file = codebase.get_file("doc.mdx")
        mdx_file.replace("test", "demo")
        codebase.commit()
        assert mdx_file.content == "# Header\nThis is a demo\nMore content"

        # Test multiple occurrences
        json_file = codebase.get_file("config.json")
        json_file.replace("test", "demo")
        codebase.commit()
        assert json_file.content == '{"demo": "value", "other": "demo"}'


def test_edit_binary_file_fails(tmpdir) -> None:
    """Test that editing binary files raises an error"""
    binary_content = bytes([0x89, 0x50, 0x4E, 0x47])  # PNG header
    with get_codebase_session(tmpdir=tmpdir, files={"image.png": binary_content}) as codebase:
        file = codebase.get_file("image.png")

        with pytest.raises(ValueError, match="Cannot replace content in binary files"):
            file.edit("new content")

        with pytest.raises(ValueError, match="Cannot replace content in binary files"):
            file.replace("old", "new")


def test_edit_source_file_preserves_behavior(tmpdir) -> None:
    """Test that source files still use TreeSitter-based editing"""
    with get_codebase_session(tmpdir=tmpdir, files={"script.py": "def test():\n    print('hello')"}) as codebase:
        file = codebase.get_file("script.py")

        # Should use TreeSitter node-based editing
        file.edit("def test():\n    print('world')")
        codebase.commit()
        assert file.content == "def test():\n    print('world')"

        # Verify the file is still parseable as Python
        assert isinstance(file, SourceFile)
        assert file.get_function("test") is not None


def test_transaction_ordering_non_source_files(tmpdir) -> None:
    """Test that transaction ordering works for non-source files"""
    with get_codebase_session(tmpdir=tmpdir, files={"doc.md": "# Header\nContent\nFooter"}) as codebase:
        file = codebase.get_file("doc.md")

        # Apply changes sequentially to avoid transaction conflicts
        file.edit("# New Header\nContent\nFooter", priority=1)
        codebase.commit()

        file.edit("# New Header\nNew Content\nFooter", priority=2)
        codebase.commit()

        file.edit("# New Header\nNew Content\nNew Footer", priority=0)
        codebase.commit()

        # Verify final content
        assert file.content == "# New Header\nNew Content\nNew Footer"
