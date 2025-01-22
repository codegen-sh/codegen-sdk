# TODO: SCRUB
import platform

import pytest

from codegen_sdk.codebase.factory.get_session import get_codebase_session
from codegen_sdk.core.function import Function
from codegen_sdk.enums import ProgrammingLanguage
from tests.utils.normalize import normalize_imports

# All the diff types of JS/TS imports:

# Module import
# import * as module from "./module";

# Named import
# import { foo, bar } from "./module";

# Default import
# import foo from "./module";

# Aliased Named import
# import { foo as baz } from "./module";

# Named with default import
# import foo, { bar, woof as bark } from "./module";

# side effect import
# import "./module";

# type import (also should work with default, alias etc)
# import type DefaultType, { Device, User as u } from "./module";

# Dynamic Import
# const module = await import("./module");


def test_move_to_file_import_star(tmpdir) -> None:
    """Test moving a symbol to a new file, where consumers import it via import *
    and also import other pieces from the original module which aren't moving
    """
    source_filename = "source.ts"
    # language=typescript
    source_content = """
export function targetFunction() {
    return "Hello World";
}
"""

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
"""

    usage_filename = "usage.ts"
    # language=typescript
    usage_content = """
import * as source from "./source";
const value1 = source.targetFunction();
const value2 = source.otherFunction();
const value3 = source.targetFunction();
"""

    # language=typescript
    expected_updated_usage_content = """
import { targetFunction } from 'destination';
import * as source from "./source";
const value1 = targetFunction();
const value2 = source.otherFunction();
const value3 = targetFunction();
"""

    files = {
        source_filename: source_content,
        dest_filename: dest_content,
        usage_filename: usage_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)
        usage_file = codebase.get_file(usage_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=False, strategy="update_all_imports")

    assert usage_file.content.strip() == expected_updated_usage_content.strip()


def test_move_to_file_named_import(tmpdir) -> None:
    """Test moving a symbol to a new file, where consumers import it via import { name }
    and also import other pieces from the original module which aren't moving
    """
    source_filename = "source.ts"
    # language=typescript
    source_content = """
export function targetFunction() {
    return "Hello World";
}
"""

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
"""

    usage_filename = "usage.ts"
    # language=typescript
    usage_content = """
import { targetFunction, otherFunction } from "./source";
const value = targetFunction();
"""

    # language=typescript
    expected_updated_usage_content = """
import { targetFunction } from 'destination';
import { otherFunction } from "./source";
const value = targetFunction();
"""

    files = {
        source_filename: source_content,
        dest_filename: dest_content,
        usage_filename: usage_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)
        usage_file = codebase.get_file(usage_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=False, strategy="update_all_imports")

    assert usage_file.content.strip() == expected_updated_usage_content.strip()


def test_move_to_file_only_named_import(tmpdir) -> None:
    """Test moving a symbol to a new file, where consumers import it via import {name}
    and don't import anything else removes that whole import line
    """
    source_filename = "source.ts"
    # language=typescript
    source_content = """
export function targetFunction() {
    return "Hello World";
}
"""

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
"""

    usage_filename = "usage.ts"
    # language=typescript
    usage_content = """
import { targetFunction } from "./source";
const value = targetFunction();
"""

    # language=typescript
    expected_updated_usage_content = """
import { targetFunction } from 'destination';
const value = targetFunction();
"""

    files = {
        source_filename: source_content,
        dest_filename: dest_content,
        usage_filename: usage_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)
        usage_file = codebase.get_file(usage_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=False, strategy="update_all_imports")

    assert usage_file.content.strip() == expected_updated_usage_content.strip()


def test_move_to_file_include_type_import_dependencies(tmpdir) -> None:
    """Test moving a symbol to a new file with type dependencies"""
    types_filename = "types.ts"
    # language=typescript
    types_content = """
export type TypeA = {
    prop: string;
}

export type TypeB = {
    value: number;
}

export type TypeC = {
    flag: boolean;
}

export function helper(input: string): string {
    return input.toUpperCase();
}
"""

    source_filename = "source.ts"
    # language=typescript
    source_content = """
import type { TypeA, TypeB, TypeC } from "types";
import { helper } from "types";

export function targetFunction(input: TypeA): TypeB {
    const value = helper(input.prop);
    return {
        value: value.length
    };
}
"""

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
"""

    # TODO: Is the extra new lines here expected behavior?
    # language=typescript
    expected_updated_dest_content = """
import type { TypeA } from 'types';
import { helper } from 'types';
import type { TypeB } from 'types';



export function targetFunction(input: TypeA): TypeB {
    const value = helper(input.prop);
    return {
        value: value.length
    };
}
"""

    files = {
        types_filename: types_content,
        source_filename: source_content,
        dest_filename: dest_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=False, strategy="update_all_imports")

    assert normalize_imports(dest_file.content.strip()) == normalize_imports(expected_updated_dest_content.strip())


def test_move_to_file_imports_local_deps(tmpdir) -> None:
    """Test moving a symbol that has dependencies on local symbols in the same file"""
    source_filename = "source.ts"
    # language=typescript
    source_content = """
export function targetFunction(value: number): number {
    return helperFunction(value) * 2;
}

function helperFunction(x: number): number {
    return x + 1;
}
"""

    dest_filename = "destination.ts"
    # language=typescript
    dest_content = """
"""

    # TODO: Is the extra new lines here expected behavior?
    # language=typescript
    expected_updated_dest_content = """
import { helperFunction } from 'source';



export function targetFunction(value: number): number {
    return helperFunction(value) * 2;
}
"""

    # language=typescript
    expected_source_content = """
export function helperFunction(x: number): number {
    return x + 1;
}
"""

    files = {
        source_filename: source_content,
        dest_filename: dest_content,
    }

    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files=files) as codebase:
        source_file = codebase.get_file(source_filename)
        dest_file = codebase.get_file(dest_filename)

        target_function = source_file.get_function("targetFunction")
        target_function.move_to_file(dest_file, include_dependencies=False, strategy="update_all_imports")

    assert normalize_imports(dest_file.content.strip()) == normalize_imports(expected_updated_dest_content.strip())
    assert normalize_imports(source_file.content.strip()) == normalize_imports(expected_source_content.strip())


# ED_TODO: Check if this test needs fixing
@pytest.mark.skip(reason="Broken. TODO: @edward will fix")
def test_move_to_file_backedge_include_deps(tmpdir) -> None:
    FOO_FILENAME = "foo_test_move_to_file.ts"
    BAR_FILENAME = "bar_test_move_to_file.ts"
    BAZ_FILENAME = "baz_test_move_to_file.ts"

    # language=typescript
    FOO_FILE_CONTENT = """
function foo(): number {
    return 1;
}
    """

    # language=typescript
    BAR_FILE_CONTENT = """
function abc(): string {
    /*dependency, gets moved*/
    return 'abc';
}

/**
 * Example function to move
 *
 * @param {number[]} numbers - An array of numerical values.
 */
function bar(): string {
    /*gets moved*/
    return abc();
}

function xyz(): number {
    /*should stay*/
    return 3;
}
    """

    # language=typescript
    BAZ_FILE_CONTENT = """
import { bar } from './bar_test_move_to_file';

function baz(): string {
    /*uses bar*/
    return bar();
}
    """

    ########################################
    # Intended Files After Move
    ########################################

    # --------------------------------------
    # foo_test_move_to_file.ts
    # --------------------------------------
    #
    # function foo(): number {
    #    return 1;
    # }
    #
    # function abc(): string {
    #    /*dependency, gets moved*/
    #    return 'abc';
    # }
    #
    # @my_decorator
    # function bar(): string {
    #    /*gets moved*/
    #    return abc();
    # }
    #

    # --------------------------------------
    # bar_test_move_to_file.ts
    # --------------------------------------
    #
    # import { bar } from './foo_test_move_to_file';
    # import { abc } from './foo_test_move_to_file';
    #
    # function xyz(): number {
    #    /*should stay*/
    #    return 3;
    # }
    #

    # --------------------------------------
    # baz_test_move_to_file.ts
    # --------------------------------------
    #
    # import { bar } from './bar_test_move_to_file';
    #
    # function baz(): string {
    #    /*uses bar*/
    #    return bar();
    # }
    #

    with get_codebase_session(
        tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={FOO_FILENAME: FOO_FILE_CONTENT, BAR_FILENAME: BAR_FILE_CONTENT, BAZ_FILENAME: BAZ_FILE_CONTENT}
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)
        baz_file = codebase.get_file(BAZ_FILENAME)

        bar_symbol = bar_file.get_symbol("bar")
        bar_symbol.move_to_file(foo_file, strategy="add_back_edge", include_dependencies=True)

    new_symbol = foo_file.get_symbol("bar")

    # Check foo_test_move_to_file
    # language=typescript
    docstring = """/**
 * Example function to move
 *
 * @param {number[]} numbers - An array of numerical values.
 */"""
    assert "function foo(): number {" in foo_file.content
    assert "function abc(): string {" in foo_file.content
    assert docstring in foo_file.content
    assert "function bar(): string {" in foo_file.content
    assert "return abc();" in foo_file.content
    assert codebase.get_symbol("foo").file == foo_file
    assert codebase.get_symbol("abc").file == foo_file
    assert codebase.get_symbol("bar").file == foo_file

    # Check bar_test_move_to_file
    assert "function abc(): string {" not in bar_file.content
    assert docstring not in bar_file.content
    assert "function bar(): string {" not in bar_file.content
    assert "return abc();" not in bar_file.content
    assert "function xyz(): number {" in bar_file.content
    assert codebase.get_symbol("xyz").file == bar_file
    assert "import { bar } from './foo_test_move_to_file';" in bar_file.content
    assert "import { abc } from './foo_test_move_to_file';" in bar_file.content

    # check baz_test_move_to_file
    assert "import { bar } from './bar_test_move_to_file';" in baz_file.content
    assert "import { bar } from './foo_test_move_to_file';" not in baz_file.content
    assert "function baz(): string {" in baz_file.content
    assert "return bar();" in baz_file.content
    assert codebase.get_symbol("baz").file == baz_file

    # Check new symbol
    assert new_symbol.file == foo_file
    assert new_symbol.name == "bar"
    assert isinstance(new_symbol, Function)


# ED_TODO: Check if this test needs fixing
@pytest.mark.skip(reason="Broken. TODO: @edward will fix")
def test_move_to_file_update_imports_include_deps(tmpdir) -> None:
    FOO_FILENAME = "foo_test_move_to_file.ts"
    BAR_FILENAME = "bar_test_move_to_file.ts"
    BAZ_FILENAME = "baz_test_move_to_file.ts"

    # language=typescript
    FOO_FILE_CONTENT = """
    function foo(): number {
        return 1;
    }
    """

    # language=typescript
    BAR_FILE_CONTENT = """
    function abc(): string {
        /*dependency, gets moved*/
        return 'abc';
    }

    @my_decorator
    function bar(): string {
        /*gets moved*/
        return abc();
    }

    function xyz(): number {
        /*should stay*/
        return 3;
    }
    """

    # language=typescript
    BAZ_FILE_CONTENT = """
    import { bar } from './bar_test_move_to_file';

    function baz(): string {
        /*uses bar*/
        return bar();
    }
    """

    ########################################
    # Intended Files After Move
    ########################################

    # --------------------------------------
    # foo_test_move_to_file.ts
    # --------------------------------------
    #
    # function foo(): number {
    #    return 1;
    # }
    #
    # function abc(): string {
    #    /*dependency, gets moved*/
    #    return 'abc';
    # }
    #
    # @my_decorator
    # function bar(): string {
    #    /*gets moved*/
    #    return abc();
    # }
    #

    # --------------------------------------
    # bar_test_move_to_file.ts
    # --------------------------------------
    #
    # function xyz(): number {
    #    /*should stay*/
    #    return 3;
    # }
    #

    # --------------------------------------
    # baz_test_move_to_file.ts
    # --------------------------------------
    #
    # import { bar } from './foo_test_move_to_file';
    #
    # function baz(): string {
    #    /*uses bar*/
    #    return bar();
    # }
    #

    with get_codebase_session(
        tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={FOO_FILENAME: FOO_FILE_CONTENT, BAR_FILENAME: BAR_FILE_CONTENT, BAZ_FILENAME: BAZ_FILE_CONTENT}
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)
        baz_file = codebase.get_file(BAZ_FILENAME)

        bar_symbol = bar_file.get_symbol("bar")
        bar_symbol.move_to_file(foo_file, strategy="update_all_imports", include_dependencies=True)

    new_symbol = foo_file.get_symbol("bar")

    # Check foo_test_move_to_file
    assert "function foo(): number {" in foo_file.content
    assert "function abc(): string {" in foo_file.content
    assert "@my_decorator" in foo_file.content
    assert "function bar(): string {" in foo_file.content
    assert "return abc();" in foo_file.content
    assert codebase.get_symbol("foo").file == foo_file
    assert codebase.get_symbol("abc").file == foo_file
    assert codebase.get_symbol("bar").file == foo_file

    # Check bar_test_move_to_file
    assert "function abc(): string {" not in bar_file.content
    assert "@my_decorator" not in bar_file.content
    assert "function bar(): string {" not in bar_file.content
    assert "return abc();" not in bar_file.content
    assert "function xyz(): number {" in bar_file.content
    assert codebase.get_symbol("xyz").file == bar_file
    assert "import { bar } from './foo_test_move_to_file';" not in bar_file.content
    assert "import { abc } from './foo_test_move_to_file';" not in bar_file.content

    # check baz_test_move_to_file
    assert "import { bar } from './foo_test_move_to_file';" in baz_file.content
    assert "function baz(): string {" in baz_file.content
    assert "return bar();" in baz_file.content
    assert codebase.get_symbol("baz").file == baz_file

    # Check new symbol
    assert new_symbol.file == foo_file
    assert new_symbol.name == "bar"
    assert isinstance(new_symbol, Function)


# ED_TODO: Check if this test needs fixing
@pytest.mark.skip(reason="Not supported yet")
def test_move_to_file_update_imports_without_include_deps(tmpdir) -> None:
    FOO_FILENAME = "foo_test_move_to_file.ts"
    BAR_FILENAME = "bar_test_move_to_file.ts"
    BAZ_FILENAME = "baz_test_move_to_file.ts"

    # language=typescript
    FOO_FILE_CONTENT = """
    function foo(): number {
        return 1;
    }
    """

    # language=typescript
    BAR_FILE_CONTENT = """
    function abc(): string {
        /*dependency, DOES NOT GET MOVED*/
        return 'abc';
    }

    @my_decorator
    function bar(): string {
        /*gets moved*/
        return abc();
    }

    function xyz(): number {
        /*should stay*/
        return 3;
    }
    """

    # language=typescript
    BAZ_FILE_CONTENT = """
    import { bar } from './bar_test_move_to_file';

    function baz(): string {
        /*uses bar*/
        return bar();
    }
    """

    ########################################
    # Intended Files After Move
    ########################################

    # --------------------------------------
    # foo_test_move_to_file.ts
    # --------------------------------------
    #
    # import { abc } from './bar_test_move_to_file';
    #
    # function foo(): number {
    #    return 1;
    # }
    #
    # @my_decorator
    # function bar(): string {
    #    /*gets moved*/
    #    return abc();
    # }
    #

    # --------------------------------------
    # bar_test_move_to_file.ts
    # --------------------------------------
    #
    # function abc(): string {
    #    /*dependency, gets moved*/
    #    return 'abc';
    # }
    #
    # function xyz(): number {
    #    /*should stay*/
    #    return 3;
    # }
    #

    # --------------------------------------
    # baz_test_move_to_file.ts
    # --------------------------------------
    #
    # import { bar } from './foo_test_move_to_file';
    #
    # function baz(): string {
    #    /*uses bar*/
    #    return bar();
    # }
    #

    with get_codebase_session(
        tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={FOO_FILENAME: FOO_FILE_CONTENT, BAR_FILENAME: BAR_FILE_CONTENT, BAZ_FILENAME: BAZ_FILE_CONTENT}
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)
        baz_file = codebase.get_file(BAZ_FILENAME)

        bar_symbol = bar_file.get_symbol("bar")
        bar_symbol.move_to_file(foo_file, strategy="update_all_imports", include_dependencies=False)

        # Check foo_test_move_to_file
        assert "function foo(): number {" in foo_file.content
        assert "function abc(): string {" not in foo_file.content
        assert "@my_decorator" in foo_file.content
        assert "function bar(): string {" in foo_file.content
        assert "return abc();" in foo_file.content
        assert codebase.get_symbol("foo").file == foo_file
        assert codebase.get_symbol("bar").file == foo_file
        assert "import { abc } from './bar_test_move_to_file';" in foo_file.content

        # Check bar_test_move_to_file
        assert "function abc(): string {" in bar_file.content
        assert "@my_decorator" not in bar_file.content
        assert "function bar(): string {" not in bar_file.content
        assert "function xyz(): number {" in bar_file.content
        assert codebase.get_symbol("abc").file == foo_file
        assert codebase.get_symbol("xyz").file == bar_file
        assert "import { bar } from './foo_test_move_to_file';" not in bar_file.content
        assert "import { abc } from './foo_test_move_to_file';" not in bar_file.content

        # check baz_test_move_to_file
        assert "import { bar } from './foo_test_move_to_file';" in baz_file.content
        assert "function baz(): string {" in baz_file.content
        assert "return bar();" in baz_file.content
        assert codebase.get_symbol("baz").file == baz_file

        # Check new symbol
        new_symbol = foo_file.get_symbol("bar")
        assert new_symbol.file == foo_file
        assert new_symbol.name == "bar"
        assert isinstance(new_symbol, Function)


def test_function_move_to_file_circular_dependency(tmpdir) -> None:
    # language=typescript
    content1 = """
export function foo(): number {
    return bar() + 1;
}

export function bar(): number {
    return foo() + 1;
}
    """
    with get_codebase_session(tmpdir, files={"file1.ts": content1}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file1 = codebase.get_file("file1.ts")
        foo = file1.get_function("foo")
        bar = file1.get_function("bar")
        assert bar in foo.dependencies
        assert foo in bar.dependencies

        file2 = codebase.create_file("file2.ts", "")
        foo.move_to_file(file2, include_dependencies=True, strategy="add_back_edge")

    # language=typescript
    assert (
        file2.content.strip()
        == """
export function bar(): number {
    return foo() + 1;
}

export function foo(): number {
    return bar() + 1;
}
""".strip()
    )
    assert file1.content.strip() == "export { bar } from 'file2'\nexport { foo } from 'file2'"


@pytest.mark.skipif(condition=platform.system() != "Linux", reason="Only works on case-sensitive file systems")
def test_function_move_to_file_lower_upper(tmpdir) -> None:
    # language=typescript
    content1 = """
export function foo(): number {
    return bar() + 1;
}

export function bar(): number {
    return foo() + 1;
}
    """
    with get_codebase_session(tmpdir, files={"file1.ts": content1}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file1 = codebase.get_file("file1.ts")
        foo = file1.get_function("foo")
        bar = file1.get_function("bar")
        assert bar in foo.dependencies
        assert foo in bar.dependencies

        file2 = codebase.create_file("File1.ts", "")
        foo.move_to_file(file2, include_dependencies=True, strategy="add_back_edge")

    # language=typescript
    assert (
        file2.content.strip()
        == """
export function bar(): number {
    return foo() + 1;
}

export function foo(): number {
    return bar() + 1;
}
""".strip()
    )
    assert file1.content.strip() == "export { bar } from 'File1'\nexport { foo } from 'File1'"


def test_function_move_to_file_no_deps(tmpdir) -> None:
    # language=typescript
    content1 = """
export function foo(): number {
    return bar() + 1;
}

export function bar(): number {
    return foo() + 1;
}
    """
    with get_codebase_session(tmpdir, files={"file1.ts": content1}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file1 = codebase.get_file("file1.ts")
        foo = file1.get_function("foo")
        bar = file1.get_function("bar")
        assert bar in foo.dependencies
        assert foo in bar.dependencies

        file2 = codebase.create_file("File2.ts", "")
        foo.move_to_file(file2, include_dependencies=False, strategy="add_back_edge")

    # language=typescript
    assert (
        file1.content.strip()
        == """import { foo } from 'File2';
export { foo }

export function bar(): number {
    return foo() + 1;
}"""
    )
    # language=typescript
    assert (
        file2.content.strip()
        == """
import { bar } from 'file1';


export function foo(): number {
    return bar() + 1;
}

""".strip()
    )


@pytest.mark.skipif(condition=platform.system() != "Linux", reason="Only works on case-sensitive file systems")
def test_function_move_to_file_lower_upper_no_deps(tmpdir) -> None:
    # language=typescript
    content1 = """
export function foo(): number {
    return bar() + 1;
}

export function bar(): number {
    return foo() + 1;
}
    """
    with get_codebase_session(tmpdir, files={"file1.ts": content1}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file1 = codebase.get_file("file1.ts")
        foo = file1.get_function("foo")
        bar = file1.get_function("bar")
        assert bar in foo.dependencies
        assert foo in bar.dependencies

        file2 = codebase.create_file("File1.ts", "")
        foo.move_to_file(file2, include_dependencies=False, strategy="add_back_edge")

    # language=typescript
    assert (
        file1.content.strip()
        == """import { foo } from 'File1';
export { foo }

export function bar(): number {
    return foo() + 1;
}"""
    )
    # language=typescript
    assert (
        file2.content.strip()
        == """
import { bar } from 'file1';


export function foo(): number {
    return bar() + 1;
}
""".strip()
    )
