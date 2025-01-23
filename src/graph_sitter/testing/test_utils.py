from collections.abc import Callable

import pytest

from graph_sitter.core.codebase import Codebase
from graph_sitter.fetch_codebase import fetch_codebase


def codemod_test(*repos: str, tmp_dir: str | None = None, shallow: bool = True):
    """Decorator that runs a test function against multiple repositories.

    Args:
        *repos: Repository names in the format "owner/repo"
        tmp_dir: Directory to clone repositories into
        shallow: Whether to do shallow clones

    Example:
        ```python
        def my_codemod(codebase: Codebase):
            # Codemod implementation here
            ...
            codebase.commit()

        @codemod_test("facebook/react")
        def test_my_codemod(codebase: Codebase):
            my_codemod(codebase)
            assert codebase.get_file("file.ts").source == "..."
        ```
    """
    if not repos:
        raise ValueError("Must specify at least one repository")

    def decorator(test_fn: Callable[[Codebase], None]):
        # Create a new function that takes repo_name and passes codebase to the original
        def test_wrapper(repo_name: str) -> None:
            # Fetch the codebase for this repo
            codebase = fetch_codebase(
                repo_name,
                tmp_dir=tmp_dir,
                shallow=shallow,
                commit_hash=None,  # Use latest commit
            )

            try:
                # Run the test with the codebase
                test_fn(codebase)
            finally:
                # Clean up
                codebase.reset()

        # Copy the name and docstring
        test_wrapper.__name__ = test_fn.__name__
        test_wrapper.__doc__ = test_fn.__doc__

        # Parametrize the wrapper
        return pytest.mark.parametrize("repo_name", repos)(test_wrapper)

    return decorator
