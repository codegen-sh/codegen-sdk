import os

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.enums import ProgrammingLanguage


def tets_remove_existing_file(tmpdir) -> None:
    # language=typescript
    content = """
function foo(bar: number): number {
    return bar;
}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file = codebase.get_file("test.ts")
        file.remove()

    assert not os.path.exists(file.filepath)


def test_remove_unused_imports_complete_removal(tmpdir):
    content = """
    import { unused1, unused2 } from './module1';
    import type { UnusedType } from './types';

    const x = 5;
    """
    expected = """
    const x = 5;
    """

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"test.ts": content}) as codebase:
        file = codebase.get_file("test.ts")
        file.remove_unused_imports()
        assert file.content.strip() == expected.strip()


def test_remove_unused_imports_partial_removal(tmpdir):
    content = """
    import { used, unused } from './module1';

    console.log(used);
    """
    expected = """
    import { used } from './module1';

    console.log(used);
    """

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"test.ts": content}) as codebase:
        file = codebase.get_file("test.ts")
        file.remove_unused_imports()
        assert file.content.strip() == expected.strip()


def test_remove_unused_imports_with_side_effects(tmpdir):
    content = """
    import './styles.css';
    import { unused } from './module1';

    const x = 5;
    """
    expected = """
    import './styles.css';

    const x = 5;
    """

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"test.ts": content}) as codebase:
        file = codebase.get_file("test.ts")
        file.remove_unused_imports()
        assert file.content.strip() == expected.strip()


def test_remove_unused_imports_with_moved_symbols(tmpdir):
    content1 = """
    import { helper } from './utils';

    export function foo() {
        return helper();
    }
    """
    expected1 = """
    export function foo() {
        return helper();
    }
    """

    content2 = """
    export function helper() {
        return true;
    }
    """

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"main.ts": content1, "utils.ts": content2}) as codebase:
        main_file = codebase.get_file("main.ts")
        foo = main_file.get_function("foo")

        # Move foo to a new file
        new_file = codebase.create_file("new.ts")
        foo.move_to_file(new_file)

        assert main_file.content.strip() == expected1.strip()
