# TODO: SCRUB
import logging
import os

import psutil
import pytest
from pytest_codspeed import BenchmarkFixture

from codegen.git.repo_operator.repo_operator import RepoOperator
from codegen.sdk.codebase.config import CodebaseConfig, DefaultFlags, ProjectConfig
from codegen.sdk.codebase.validation import PostInitValidationStatus, post_init_validation
from codegen.sdk.core.codebase import Codebase
from tests.shared.codemod.models import Repo
from tests.shared.utils.recursion import set_recursion_limit

BYTES_IN_GIGABYTE = 1024**3
MAX_ALLOWED_GIGABYTES = 31
logger = logging.getLogger(__name__)


@pytest.mark.timeout(60 * 12, func_only=True)
def test_codemods_parse(repo: Repo, op: RepoOperator, request, codspeed_benchmark: BenchmarkFixture) -> None:
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
    codebase = codspeed_benchmark(lambda: Codebase(projects=projects, config=config))
    memory_used = psutil.Process(os.getpid()).memory_info().rss
    codspeed_benchmark.extra_info["memory_used"] = memory_used
    logger.info(f"Using {memory_used / BYTES_IN_GIGABYTE} GB of memory.")
    assert memory_used <= BYTES_IN_GIGABYTE * MAX_ALLOWED_GIGABYTES, "Graph is using too much memory!"
    validation_res = post_init_validation(codebase)
    if validation_res != PostInitValidationStatus.SUCCESS:
        msg = f"Graph failed post init validation: {validation_res}!"
        raise Exception(msg)
