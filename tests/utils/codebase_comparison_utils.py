import difflib
import filecmp
import logging
import subprocess
import tempfile
from pathlib import Path

from Levenshtein import distance as levenshtein_distance
from pytest_snapshot.plugin import Snapshot

from codegen_git.schemas.enums import DiffChangeType
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.testing.constants import DIFF_FILEPATH

logger = logging.getLogger(__name__)


def unflatten_to_dict(original: dict[Path, str]) -> dict[str, dict | str]:
    # This is mildly cursed but needed for pytest-snapshot
    new: dict = {}
    for file, content in original.items():
        parts = [part for part in file.parts if part != ""]
        current = new
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = content
    return new


def gather_modified_files(codebase: Codebase) -> dict[Path, str]:
    """Gather all modified files in the codebase."""
    modified = {}
    for diff_file in codebase.get_diffs():
        file_path = Path(diff_file.a_path)
        if "__pycache__" in file_path.parts:
            continue
        if file_path.is_absolute():
            original = file_path
            relative = file_path.relative_to(codebase.repo_path)
        else:
            original = codebase.repo_path / file_path
            relative = file_path
        match diff_file.change_type:
            case DiffChangeType.MODIFIED.value | DiffChangeType.ADDED.value:
                modified[relative] = original.read_text()
    return modified


def convert_diff_to_repo(test_dir: Path, diff_file: Path, codebase: Codebase) -> bool:
    """Turns git diffs into an expected directory for easier debugging"""
    with diff_file.open(mode="r") as diff_file_obj:
        assert diff_file_obj.read().strip(), "Expected Diff is Empty!!!"
    subprocess.run(["git", "apply", str(diff_file.absolute())], cwd=codebase.repo_path)
    to_copy = gather_modified_files(codebase)
    if len(to_copy) == 0:
        # This prevents deletion of failed patches
        logger.info("Could not find modified files")
        return False
    for file, text in to_copy.items():
        new_path = test_dir / file
        new_path.parent.mkdir(parents=True, exist_ok=True)
        new_path.write_text(text)
    codebase.reset()
    return True


def compare_codebase_diff(
    codebase: Codebase,
    expected_dir: Path,
    diff_path: Path,
    expected_diff: Path,
    snapshot: Snapshot,
) -> None:
    diff = codebase.get_diff() + "\n"
    if not snapshot._snapshot_update:
        modified = gather_modified_files(codebase)
        codebase.reset()
        logger.info("Converting diff file to expected repository")
        if convert_diff_to_repo(expected_dir, expected_diff, codebase):
            return compare_codebase_with_snapshot(codebase, expected_dir, diff_path, snapshot, modified)
    # === [Snapshot Comparison] ===
    snapshot.snapshot_dir = expected_diff.parent
    assert diff.strip() != "", "No diff was generated"
    snapshot.assert_match(diff.strip(), DIFF_FILEPATH)


def compare_codebase_with_snapshot(codebase: Codebase, expected_dir: Path, diff_path: Path, snapshot: Snapshot, modified, capture_stats: bool = False, extensions: set = ".py") -> None:
    """Compare the expected codebase to the modified codebase."""
    if not expected_dir.exists():
        logger.warning(f"There is no result to compare this test case to. {expected_dir} does not exist")
        return

    codebase_path = codebase.repo_path

    # === [Snapshot Comparison] ===
    snapshot.snapshot_dir = expected_dir.parent
    if not snapshot._snapshot_update and expected_dir.is_dir():
        analyze_codebase_diff(expected_dir, codebase_path, diff_path, extensions, capture_stats)
    snapshot.assert_match_dir(unflatten_to_dict(modified), expected_dir.name)


def compare_expected_actual_diffs(codebase: Codebase, actual_diff: str, expected_diff: str, extensions: set[str] = {".py"}) -> str:
    """Compare the expected codebase to the modified codebase."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        tmp_dir = Path(tmp_dir)
        # === [Create Expected Directory] ===
        expected_dir = tmp_dir / "expected_dir"
        expected_dir.mkdir(parents=True, exist_ok=True)

        # === [Create Actual Diff File] ===
        actual_diff_path = tmp_dir / "actual_diff.txt"
        actual_diff_path.write_text(actual_diff + "\n")  # Extra '\n\ necessary for git to apply the diff

        # === [Create Expected Diff File] ===
        expected_diff_path = tmp_dir / DIFF_FILEPATH
        expected_diff_path.write_text(expected_diff + "\n")  # Extra '\n\ necessary for git to apply the diff

        # ===== [ Reset Codebase and Apply Expected Diff ] =====
        codebase.reset()
        if convert_diff_to_repo(expected_dir, expected_diff_path, codebase):
            # === [Apply Actual Diff to Codebase] ===
            subprocess.run(["git", "apply", str(actual_diff_path.absolute())], cwd=codebase.repo_path)
        else:
            raise ValueError("failed to convert diff to repo")

        # === [Generate a Diff of Diffs] ===
        analyze_codebase_diff(expected_dir, codebase.repo_path, tmp_dir, extensions, capture_stats=False, single_diff_file=True)

        diff_file_path = (tmp_dir / "diff_of_diffs.html").absolute()
        with diff_file_path.open(mode="r", encoding="utf-8") as diff_file:
            diff_of_diffs = diff_file.read()
            return diff_of_diffs


def capture_single_file_stats(files_dir: Path, files, expected_dir: Path, extensions: set, diff_stats: dict) -> list[str]:
    """Captures stats on files that exist in one codebase but not the other."""
    diff = []
    for filename in files:
        if filename.endswith(tuple(extensions)):
            left_file = files_dir / filename
            relative_path = left_file.relative_to(expected_dir)
            diff.append(f"File {relative_path} was removed")
            with open(left_file) as f:
                lines = f.readlines()
            diff_stats["lines_removed"] += len(lines)
    return diff


def capture_modified_file_stats(left_lines: list[str], right_lines: list[str], diff_stats: dict):
    """Captures stats on the differences between two complementary files, a file that
    exists in both the expected and modified codebases.
    """
    matcher = difflib.SequenceMatcher(None, left_lines, right_lines)
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == "insert":
            diff_stats["lines_added"] += j2 - j1
        elif opcode == "delete":
            diff_stats["lines_removed"] += i2 - i1
        elif opcode == "replace":
            diff_stats["lines_modified"] += max(i2 - i1, j2 - j1)
            for old_line, new_line in zip(left_lines[i1:i2], right_lines[j1:j2]):
                diff_stats["edit_distance"] += levenshtein_distance(old_line, new_line)


def analyze_codebase_diff(expected_dir: Path, modified_dir: Path, diff_path: Path, extensions: set[str] = {".py"}, capture_stats: bool = False, single_diff_file: bool = False) -> dict | None:
    """Generate and analyze the diff between the expected and modified codebases. If capture_stats is True,
    detailed stats on the diff will be captured and returned.
    """
    if capture_stats:
        diff_stats = {"lines_added": 0, "lines_removed": 0, "lines_modified": 0, "edit_distance": 0, "diff": ""}
        diff = []
    else:
        diff_stats = None
        diff = None

    # === [Compare the Codebases] ===
    dcmp = filecmp.dircmp(expected_dir, modified_dir)

    def process_diff(left_dir: Path, right_dir: Path, common_files: list, left_only: list, right_only: list, subdirs: dict, resulting_diff: str = ""):
        # === [Compare Files Existing in both the Modified and Expected Codebase] ===
        for filename in common_files:
            if not filename.endswith(tuple(extensions)):
                continue

            left_file = left_dir / filename
            right_file = right_dir / filename
            relative_path = left_file.relative_to(expected_dir)

            # === [Compare File Contents] ===
            if not filecmp.cmp(left_file, right_file, shallow=False):
                with open(left_file) as f:
                    left_lines = f.readlines()
                with open(right_file) as f:
                    right_lines = f.readlines()

                # === [Generate & Save Html Diff File] ===
                html_diff = difflib.HtmlDiff().make_file(left_lines, right_lines, fromdesc="expected", todesc="actual", context=True)
                if single_diff_file:
                    file_path = relative_path / filename
                    resulting_diff += f"<h2>Diff for {file_path!s}</h2>" + "\n" + html_diff + "\n"
                else:
                    (diff_path / str(relative_path)).with_suffix(".html").parent.mkdir(parents=True, exist_ok=True)
                    (diff_path / str(relative_path)).with_suffix(".html").write_text(html_diff)

                # === [Capture Detailed Stats on the Diffs] ===
                if capture_stats:
                    file_diff = list(difflib.unified_diff(left_lines, right_lines, fromfile=str(relative_path), tofile=str(relative_path)))
                    diff.extend(file_diff)
                    capture_modified_file_stats(left_lines, right_lines, diff_stats)

        # === [Capture Stats on Files without a Complement] ===
        if capture_stats:
            left_diff = capture_single_file_stats(left_dir, left_only, expected_dir, extensions, diff_stats)
            right_diff = capture_single_file_stats(right_dir, right_only, modified_dir, extensions, diff_stats)
            diff.extend(left_diff)
            diff.extend(right_diff)

        # === [Recursively Process Subdirectories] ===
        for subdir, subdir_dcmp in subdirs.items():
            resulting_diff = process_diff(left_dir / subdir, right_dir / subdir, subdir_dcmp.common_files, subdir_dcmp.left_only, subdir_dcmp.right_only, subdir_dcmp.subdirs, resulting_diff)
        return resulting_diff

    # === [Process the Diff] ===
    resulting_diff = process_diff(expected_dir, modified_dir, dcmp.common_files, dcmp.left_only, dcmp.right_only, dcmp.subdirs)

    if single_diff_file:
        (diff_path / "diff_of_diffs").with_suffix(".html").write_text(resulting_diff)

    if capture_stats:
        diff_stats["diff"] = "\n".join(diff)
        return diff_stats
    else:
        return None
