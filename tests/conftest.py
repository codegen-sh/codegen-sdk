import logging
import os
from pathlib import Path

import pytest

from tests.shared.codemod.models import Size


def find_dirs_to_ignore(start_dir, prefix):
    dirs_to_ignore = []
    for root, dirs, files in os.walk(start_dir):
        for dir in dirs:
            full_path = os.path.relpath(os.path.join(root, dir), start_dir)
            if any(dd.startswith("original_input") or dd.startswith("output") or dd.startswith("input") or dd.startswith("expected") for dd in dir.split("/")):
                dirs_to_ignore.append(full_path)
    return dirs_to_ignore


def pytest_addoption(parser):
    parser.addoption(
        "--size",
        action="append",
        type=Size,
        default=["small"],
        choices=map(str.lower, Size.__members__.keys()),
        help="What size test cases to run",
    )
    parser.addoption(
        "--profile",
        action="store",
        type=bool,
        default=False,
        help="Whether to profile the test",
    )
    parser.addoption(
        "--sync-graph",
        action="store",
        type=str,
        dest="sync-graph",
        default="false",
        help="Whether to sync the graph between tests",
    )
    parser.addoption(
        "--log-parse",
        action="store",
        type=str,
        dest="log-parse",
        default="false",
        help="Whether to log parsing errors for parse tests",
    )
    parser.addoption(
        "--extra-repos",
        type=bool,
        action="store",
        default=False,
        help="Whether to test on extra repos",
    )
    parser.addoption("--token", action="store", default=None, help="Read-only GHA token to access extra repos")

    parser.addoption("--codemod-id", action="store", type=int, default=None, help="Runs db skills test for a specific codemod")

    parser.addoption("--repo-id", action="store", type=int, default=None, help="Runs db skills test for a specific repo")

    parser.addoption("--base-commit", action="store", type=str, default=None, help="Runs db skills test for a specific commit. Argument can be the shortest unique substring.")

    parser.addoption("--cli-api-key", action="store", type=str, default=None, help="Token necessary to access skills.")


# content of conftest.py
def pytest_configure(config):
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id is not None:
        os.makedirs("build/logs", exist_ok=True)
        logging.basicConfig(
            format=config.getini("log_file_format"),
            filename=f"build/logs/tests_{worker_id}.log",
            level=config.getini("log_file_level"),
        )


def is_git_lfs_pointer(file_path: Path) -> bool:
    """Check if a file is a git LFS pointer file"""
    try:
        with open(file_path) as f:
            first_line = f.readline().strip()
            return first_line == "version https://git-lfs.github.com/spec/v1"
    except Exception:
        return False


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        if "NodeJS or npm is not installed" in str(report.longrepr):
            pytest.skip("Test requires NodeJS and npm to be installed")


@pytest.fixture(autouse=True)
def skip_lfs_tests(request):
    """Skip tests that depend on git LFS files if they haven't been pulled"""
    # Get the test module path
    test_path = Path(request.module.__file__)

    # Only run for integration tests
    if not str(test_path).startswith(str(Path.cwd() / "tests" / "integration")):
        return

    # Get the expected diff path from the test's expected fixture
    expected = request.getfixturevalue("expected")
    if isinstance(expected, Path) and is_git_lfs_pointer(expected):
        pytest.skip(f"Test requires git LFS file {expected} which hasn't been pulled")
