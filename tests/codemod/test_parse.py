# TODO: SCRUB
import logging
import os

import psutil
import pytest

from codegen_git.repo_operator.repo_operator import RepoOperator
from graph_sitter.codebase.config import CodebaseConfig, DefaultFlags, ProjectConfig
from graph_sitter.codebase.validation import PostInitValidationStatus, post_init_validation
from graph_sitter.core.codebase import Codebase
from graph_sitter.testing.models import Repo
from tests.utils.recursion import set_recursion_limit

BYTES_IN_GIGABYTE = 1024**3
MAX_ALLOWED_GIGABYTES = 31
logger = logging.getLogger(__name__)


@pytest.mark.timeout(60 * 12, func_only=True)
def test_codemods_parse(repo: Repo, op: RepoOperator, request) -> None:
    # Setup Feature Flags
    if repo.feature_flags is not None:
        feature_flags = repo.feature_flags
    else:
        feature_flags = DefaultFlags

    sync = request.config.getoption("sync-graph").lower() == "true"
    log_parse = request.config.getoption("log-parse").lower() == "true"
    # Update feature flags using model_copy(), since the original are frozen
    feature_flags = feature_flags.model_copy(
        update={
            "verify_graph": sync,  # Override default for sync/verify_graph
            "debug": log_parse,  # Override default for debug
            "ignore_process_errors": False,  # Force errors to be raised for testing
        }
    )
    set_recursion_limit()
    # Setup Codebase
    config = CodebaseConfig(feature_flags=feature_flags)
    projects = [ProjectConfig(repo_operator=op, programming_language=repo.language, subdirectories=repo.subdirectories)]
    codebase = Codebase(projects=projects, config=config)
    process = psutil.Process(os.getpid())
    memory_used = process.memory_info().rss
    logger.info(f"Using {memory_used / BYTES_IN_GIGABYTE} GB of memory.")
    assert memory_used <= BYTES_IN_GIGABYTE * MAX_ALLOWED_GIGABYTES, "Graph is using too much memory!"
    validation_res = post_init_validation(codebase)
    if validation_res != PostInitValidationStatus.SUCCESS:
        raise Exception(f"Graph failed post init validation: {validation_res}!")
