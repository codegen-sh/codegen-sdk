from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.enums import ProgrammingLanguage


def test_move_to_file_removes_unused_imports(tmpdir) -> None:
    """Test that moving a symbol removes unused imports when remove_unused_imports=True"""
    source_filename = "source.ts"
    # language=typescript
    source_content = """
    import { helperUtil } from './utils';
    import { otherUtil } from './other';

    export function targetFunction() {
        return helperUtil("test");
    }
    """

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
    """

    files = {
        source_filename: source_content,
        dest_filename: dest_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=True, strategy="update_all_imports", remove_unused_imports=True)

    # Verify helperUtil import was moved but otherUtil import was unaffected
    assert "import { helperUtil } from './utils';" not in source_file.content
    assert "import { otherUtil } from './other';" in source_file.content
    assert "import { helperUtil } from './utils';" in dest_file.content


def test_move_to_file_removes_unused_imports_multiline(tmpdir) -> None:
    """Test removing unused imports from multiline import statements"""
    source_filename = "source.ts"
    # language=typescript
    source_content = """
    import {
        helperUtil,
        formatUtil,
        parseUtil,
        unusedUtil
    } from './utils';
    import { otherUtil } from './other';

    export function targetFunction() {
        const formatted = formatUtil(helperUtil("test"));
        return parseUtil(formatted);
    }
    """

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
    """
    files = {
        source_filename: source_content,
        dest_filename: dest_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=True, strategy="update_all_imports", remove_unused_imports=True)

    # Verify only used imports were moved
    assert "unusedUtil" not in source_file.content
    assert "otherUtil" in source_file.content
    assert "helperUtil" in dest_file.content
    assert "formatUtil" in dest_file.content
    assert "parseUtil" in dest_file.content
    assert "unusedUtil" not in dest_file.content


def test_move_to_file_removes_unused_imports_with_aliases(tmpdir) -> None:
    """Test removing unused imports with aliases"""
    source_filename = "source.ts"
    # language=typescript
    source_content = """
    import { helperUtil as helper } from './utils';
    import { formatUtil as fmt, parseUtil as parse } from './formatters';
    import { validateUtil as validate } from './validators';

    export function targetFunction() {
        return helper(fmt("test"));
    }
    """

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
    """

    files = {
        source_filename: source_content,
        dest_filename: dest_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=True, strategy="update_all_imports", remove_unused_imports=True)

    # Verify only used aliased imports were moved
    assert "helper" not in source_file.content
    assert "fmt" not in source_file.content
    assert "parse" not in source_file.content
    assert "validate" in source_file.content
    assert "helper" in dest_file.content
    assert "fmt" in dest_file.content
    assert "parse" not in dest_file.content


def test_move_to_file_removes_unused_type_imports(tmpdir) -> None:
    """Test removing unused type imports"""
    source_filename = "source.ts"
    # language=typescript
    source_content = """
    import type { HelperOptions } from './types';
    import type { FormatConfig, ParseConfig } from './config';
    import { helperUtil } from './utils';

    export function targetFunction(options: HelperOptions) {
        return helperUtil("test", options);
    }
    """

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
    """

    files = {
        source_filename: source_content,
        dest_filename: dest_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=True, strategy="update_all_imports", remove_unused_imports=True)

    # Verify only used type imports were moved
    assert "HelperOptions" not in source_file.content
    assert "FormatConfig" in source_file.content
    assert "ParseConfig" in source_file.content
    assert "helperUtil" not in source_file.content
    assert "HelperOptions" in dest_file.content
    assert "helperUtil" in dest_file.content


def test_move_to_file_removes_unused_default_imports(tmpdir) -> None:
    """Test removing unused default imports"""
    source_filename = "source.ts"
    # language=typescript
    source_content = """
    import defaultHelper from './helper';
    import unusedDefault from './unused';
    import { namedHelper } from './utils';

    export function targetFunction() {
        return defaultHelper(namedHelper("test"));
    }
    """

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
    """

    files = {
        source_filename: source_content,
        dest_filename: dest_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=True, strategy="update_all_imports", remove_unused_imports=True)

    # Verify only used imports were moved
    assert "defaultHelper" not in source_file.content
    assert "unusedDefault" in source_file.content
    assert "namedHelper" not in source_file.content
    assert "defaultHelper" in dest_file.content
    assert "namedHelper" in dest_file.content
