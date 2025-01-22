from pathlib import Path
from typing import TypeVar

import pytest
from pytest_snapshot.plugin import Snapshot

from codegen_sdk.codemod import Codemod3
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.testing.models import BASE_PATH
from tests.utils.codebase_comparison_utils import compare_codebase_diff

DIFF_ROOT = BASE_PATH / ".diffs"
T = TypeVar("T")


@pytest.mark.timeout(120, func_only=True)
def test_codemods_cloned_repos(codemod: Codemod3, codebase: Codebase, expected: Path, tmp_path: Path, diff_folder: Path, snapshot: Snapshot) -> None:
    codemod.execute(codebase)
    codebase.commit(codebase.G.config.feature_flags.verify_graph)
    compare_codebase_diff(codebase=codebase, expected_dir=tmp_path, expected_diff=expected, diff_path=diff_folder, snapshot=snapshot)
    if codebase.G.config.feature_flags.verify_graph:
        codebase.reset()
