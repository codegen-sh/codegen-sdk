from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.enums import ProgrammingLanguage


def test_ts_import_is_dynamic_in_function_declaration(tmpdir):
    # language=typescript
    content = """
    import { staticImport } from './static';

    function loadModule() {
        import('./dynamic').then(module => {
            console.log(module);
        });
    }
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file = codebase.get_file("test.ts")
        imports = file.imports

        assert not imports[0].is_dynamic  # static import
        assert imports[1].is_dynamic  # dynamic import in function


def test_ts_import_is_dynamic_in_method_definition(tmpdir):
    # language=typescript
    content = """
    import { Component } from '@angular/core';

    class MyComponent {
        async loadFeature() {
            const feature = await import('./feature');
        }

        @Decorator()
        async decoratedMethod() {
            const module = await import('./decorated');
        }
    }
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file = codebase.get_file("test.ts")
        imports = file.imports

        assert not imports[0].is_dynamic  # static import
        assert imports[1].is_dynamic  # dynamic import in method
        assert imports[2].is_dynamic  # dynamic import in decorated method


def test_ts_import_is_dynamic_in_arrow_function(tmpdir):
    # language=typescript
    content = """
    import { useState } from 'react';

    const MyComponent = () => {
        const loadModule = async () => {
            const module = await import('./lazy');
        };

        return <button onClick={loadModule} />;
    };
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file = codebase.get_file("test.ts")
        imports = file.imports

        assert not imports[0].is_dynamic  # static import
        assert imports[1].is_dynamic  # dynamic import in async arrow function


def test_ts_import_is_dynamic_in_if_statement(tmpdir):
    # language=typescript
    content = """
    import { isFeatureEnabled } from './utils';

    if (isFeatureEnabled('feature')) {
        import('./feature').then(module => {
            module.enableFeature();
        });
    } else {
        import('./fallback').then(module => {
            module.useFallback();
        });
    }
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file = codebase.get_file("test.ts")
        imports = file.imports

        assert not imports[0].is_dynamic  # static import
        assert imports[1].is_dynamic  # dynamic import in if block
        assert imports[2].is_dynamic  # dynamic import in else block


def test_ts_import_is_dynamic_in_try_statement(tmpdir):
    # language=typescript
    content = """
    import { logger } from './logger';

    try {
        const module = await import('./main');
    } catch (error) {
        const fallback = "hello"
    } finally {
        const cleanup = "hello"
    }
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file = codebase.get_file("test.ts")
        imports = file.imports

        assert not imports[0].is_dynamic  # static import
        assert imports[1].is_dynamic  # dynamic import in try block
