import io
import json
import logging
import os
import select
import subprocess
import time

from unidiff import PatchedFile, PatchSet

from codegen.utils.performance.stopwatch_utils import stopwatch

logger = logging.getLogger(__name__)

HIGHLIGHTED_DIFF_FILENAME = "highlighted_diff.json"


@stopwatch
def syntax_highlight_modified_files(codebase, raw_diff: str, flags: list[dict]) -> str:
    modified_files = PatchSet(io.StringIO(raw_diff))
    highlighted_files = {}
    highlighted_diff_files = {}

    # TODO: refactor this
    with subprocess.Popen(
        ". ~/.bashrc > /dev/null && nvm use > /dev/null && yarn run --silent highlight",
        shell=True,
        cwd="/codegen/codegen-frontend/app/modules/syntaxHighlight",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    ) as highlighter:
        poll = select.poll()
        poll.register(highlighter.stdout, select.POLLIN)

        for file in modified_files:
            filename = file.path
            modified_filename = file.target_file
            highlighted_files[filename] = (
                "" if file.is_removed_file else _highlight_file(highlighter, poll, modified_filename if not modified_filename.startswith("b/") else modified_filename[2:], flags)
            )

        codebase.stash_changes()

        for file in modified_files:
            filename = file.path
            original_filename = file.source_file
            original = "" if file.is_added_file else _highlight_file(highlighter, poll, original_filename if not original_filename.startswith("a/") else original_filename[2:], flags)
            modified = highlighted_files[filename]
            highlighted_hunks = _construct_diff_highlight(codebase, original.splitlines(), modified.splitlines(), file)
            highlighted_diff_files[filename] = highlighted_hunks

        try:
            codebase.restore_stashed_changes()
        except Exception as e:
            # This can happen if there are no changes stashed in the first place
            logger.warning(f"Error restoring stashed changes: {e}")

        _, err = highlighter.communicate()
        returncode = highlighter.returncode

        if err:
            logger.error(f"Highlighter exited with error: {err}")

        if returncode != 0:
            raise Exception(f"Highlighter exited with code {returncode}")

    highlighted_diff = json.dumps(highlighted_diff_files)
    logger.info(f"Generated highlighted diff (size={len(highlighted_diff)})")
    return highlighted_diff


@stopwatch
def _highlight_file(highlighter: subprocess.Popen[str], poll: select.poll, filename: str, flags: list[dict]):
    stdin_input = {
        "file": f"{os.getcwd()}/{filename}",
        "flags": list(filter(lambda flag: flag["filepath"] == filename, flags)),
    }
    stdin_input = json.dumps(stdin_input)

    logger.info(f"> Highlighting {filename}...")
    highlighter.stdin.write(f"{stdin_input}\n")
    highlighter.stdin.flush()
    highlighted = ""

    while True:
        # if monotonic.monotonic() > timeout_at:
        #     raise Exception("Syntax highlighter timed out")
        #
        # poll_result = poll.poll(0.01)
        #
        # if not poll_result:
        #     continue

        # TODO: this can deadlock in case the subprocess does not write a newline
        line = highlighter.stdout.readline()

        if not line:
            time.sleep(0.01)

        if line == "\x03\n":
            break

        highlighted += line

    return highlighted


def _construct_diff_highlight(codebase, source: list[str], target: list[str], patched_file: PatchedFile) -> list:
    original_lines = 0
    modified_lines = 0
    full_file = ""
    full_file_lines = 0
    highlighted_hunks = []

    for hunk in patched_file:
        hunk_lines = ""

        while original_lines < (hunk.source_start - 1):
            full_file += f" {source[original_lines]}\n"
            full_file_lines += 1
            original_lines += 1
            modified_lines += 1

        for line in hunk:
            if line.is_removed:
                full_file += f"-{source[original_lines]}\n"
                hunk_lines += f"-{source[original_lines]}\n"
                original_lines += 1
                full_file_lines += 1
            elif line.is_added:
                full_file += f"+{target[modified_lines]}\n"
                hunk_lines += f"+{target[modified_lines]}\n"
                modified_lines += 1
                full_file_lines += 1
            else:
                if len(source) > original_lines:
                    full_file += f" {source[original_lines]}\n"
                    hunk_lines += f" {source[original_lines]}\n"
                elif len(target) > modified_lines:
                    full_file += f" {target[modified_lines]}\n"
                    hunk_lines += f" {target[modified_lines]}\n"
                else:
                    logger.warning(f"Lines {original_lines}/{modified_lines} not found in {patched_file.path} in {codebase.current_commit.hexsha}: {line}")
                original_lines += 1
                modified_lines += 1
                full_file_lines += 1

        if hunk_lines.endswith("\n"):
            hunk_lines = hunk_lines[:-1]

        highlighted_hunks.append({"lines": hunk_lines, "starts_at": full_file_lines - len(hunk), "ends_at": full_file_lines - 1})

    if original_lines < len(source):
        full_file += "\n ".join(source[original_lines:])

    # TODO: we know the file length so we can add a property to diff and determine if we can expand down even if we haven't loaded the entire file on FE yet

    return highlighted_hunks
