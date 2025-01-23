import io
import logging
from contextlib import redirect_stderr, redirect_stdout

import pytest

from codegen.sdk.code_generation.current_code_codebase import import_all_graph_sitter_modules


@pytest.mark.skip("broken after repo split, fix or move over")
def test_get_documented_objects():
    """Test that importing everything in graph-sitter
    doesn't invoke any functionality (incase someone leaves actual
    functionality at the top level of a file).

    Use no logs as a proxy for nothing bad happening
    """
    # Capture stdout and stderr
    stdout = io.StringIO()
    stderr = io.StringIO()

    logger = logging.getLogger("test_logger")

    with redirect_stdout(stdout), redirect_stderr(stderr):
        import_all_graph_sitter_modules()

    assert stdout.getvalue() == "", "Logs were written to stdout"
    assert stderr.getvalue() == "", "Logs were written to stderr"
