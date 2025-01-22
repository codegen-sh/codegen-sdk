# Overview

`codegen-backend/codegen_tests` are where we store unit tests. We store integration tests in `codegen-backend/codegen_integration`.

TODO: update the test structure to:

```
/tests
-> /unit
-> /integration
```

## Test Categories

There are three categories of tests (each in their own folder):

- [codegen_tests/codegen_sdk](codegen_sdk/README.md) -> tests for GraphSitter and Codebase
- [codegen_tests/rojects](projects/README.md) -> tests for hardcoded Codemods (i.e. the ones stored in `codegen-backend/app/projects`)
- [codegen_tests/app](app/README.md) -> everything else 💀

## Helpers

Lots of overlap between these two and at some point we should consolidate into one `/utils` folder.

- [codegen_tests/utils](utils) -> utils for setting up/writing tests (ex: creating mock files)
- [codegen_tests/mocks](mocks) -> common mocks

## Testing Guidelines

### Category Guidelines

Category specific testing guidelines can be found in the respective READMEs.

- [codegen_sdk README](codegen_sdk/README.md)
- [projects README](projects/README.md)
- [app README](app/README.md)

### General Guidelines

The following are guidelines that apply to all tests:

- Do not instantiate a DB in unit tests (ex: with `db = get_session_local()` or with `with db_context() as db`, etc)
- Use [tmpdir](https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture) where possible (handles cleaning up test files)
