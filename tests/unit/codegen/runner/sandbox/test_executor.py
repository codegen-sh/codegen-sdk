from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from codegen.git.models.codemod_context import CodemodContext
from codegen.runner.models.codemod import GroupingConfig
from codegen.sdk.codebase.config import SessionOptions
from codegen.sdk.codebase.flagging.code_flag import CodeFlag
from codegen.sdk.codebase.flagging.groupers.enums import GroupBy
from codegen.shared.compilation.string_to_code import create_execute_function_from_codeblock

if TYPE_CHECKING:
    from codegen.runner.sandbox.executor import SandboxExecutor


@pytest.mark.asyncio
async def test_execute_func_pass_in_codemod_context_takes_priority(executor: SandboxExecutor):
    codemod_context = CodemodContext(
        CODEMOD_LINK="http://codegen.sh/codemod/5678",
    )
    mock_source = """
print(context.CODEMOD_LINK)
"""
    custom_scope = {"context": codemod_context}
    code_to_exec = create_execute_function_from_codeblock(codeblock=mock_source, custom_scope=custom_scope)
    mock_log = MagicMock()
    executor.codebase.log = mock_log

    result = await executor.execute(code_to_exec)

    assert result is not None

    assert mock_log.call_count == 1
    assert mock_log.call_args_list[0][0][0] == "http://codegen.sh/codemod/5678"


# @pytest.mark.asyncio
# async def test_init_execute_func_with_pull_request_context(executor: SandboxExecutor):
#     mock_source = """
# print(context.PULL_REQUEST.head.ref)
# print(context.PULL_REQUEST.base.ref)
# """
#     mock_cm_run = MagicMock(epic=MagicMock(id=1234, link="link", user=MagicMock(github_username="user")), codemod_version=MagicMock(source=mock_source))
#     mock_pull = MagicMock(spec=GithubWebhookPR, head=MagicMock(ref="test-head"), base=MagicMock(ref="test-base"))
#     codemod_context = get_codemod_context(cm_run=mock_cm_run, pull_request=mock_pull)
#     custom_scope = {"context": codemod_context}
#     code_to_exec = create_execute_function_from_codeblock(codeblock=mock_source, custom_scope=custom_scope)
#     mock_log = MagicMock()
#     executor.codebase.log = mock_log
#
#     result = await executor.execute(code_to_exec)
#
#     assert result is not None
#     assert mock_log.call_count == 2
#     assert mock_log.call_args_list[0][0][0] == "test-head"
#     assert mock_log.call_args_list[1][0][0] == "test-base"
#
#
# @pytest.mark.asyncio
# async def test_init_execute_func_with_pull_request_context_mock_codebase(executor: SandboxExecutor):
#     mock_source = """
# print(context.PULL_REQUEST.head.ref)
# print(context.PULL_REQUEST.base.ref)
#     """
#     mock_cm_run = MagicMock(epic=MagicMock(id=1234, link="link", user=MagicMock(github_username="user")), codemod_version=MagicMock(source=mock_source))
#     mock_pull = MagicMock(spec=GithubWebhookPR, head=MagicMock(ref="test-head"), base=MagicMock(ref="test-base"))
#     codemod_context = get_codemod_context(cm_run=mock_cm_run, pull_request=mock_pull)
#     custom_scope = {"context": codemod_context}
#     code_to_exec = create_execute_function_from_codeblock(codeblock=mock_source, custom_scope=custom_scope)
#
#     result = await executor.execute(code_to_exec)
#
#     # validate
#     assert result is not None
#     assert (
#         result.logs
#         == """
# test-head
# test-base
# """.lstrip()
#     )


@pytest.mark.asyncio
async def test_run_max_preview_time_exceeded_sets_observation_meta(executor: SandboxExecutor):
    mock_source = """
codebase.files[0].edit("a = 2")
"""
    code_to_exec = create_execute_function_from_codeblock(codeblock=mock_source)
    result = await executor.execute(code_to_exec, session_options=SessionOptions(max_seconds=0))

    assert result.is_complete
    assert result.observation_meta == {"flags": [], "stop_codemod_exception_type": "MaxPreviewTimeExceeded", "threshold": 0}


@pytest.mark.asyncio
async def test_run_max_ai_requests_error_sets_observation_meta(executor: SandboxExecutor):
    mock_source = """
codebase.ai("tell me a joke")
"""
    code_to_exec = create_execute_function_from_codeblock(codeblock=mock_source)
    result = await executor.execute(code_to_exec, session_options=SessionOptions(max_ai_requests=0))

    assert result.is_complete
    assert result.observation_meta == {"flags": [], "stop_codemod_exception_type": "MaxAIRequestsError", "threshold": 0}


@pytest.mark.asyncio
async def test_run_max_transactions_exceeded_sets_observation_meta(executor: SandboxExecutor):
    mock_source = """
codebase.files[0].edit("a = 2")
"""

    code_to_exec = create_execute_function_from_codeblock(codeblock=mock_source)
    result = await executor.execute(code_to_exec, session_options=SessionOptions(max_transactions=0))

    assert result.is_complete
    assert result.observation_meta == {"flags": [], "stop_codemod_exception_type": "MaxTransactionsExceeded", "threshold": 0}


@pytest.mark.asyncio
async def test_find_flag_groups_with_subdirectories(executor: SandboxExecutor):
    groups = await executor.find_flag_groups(
        code_flags=[
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir1/file1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir2/file1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir3/file1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir3/file2.py")),
                message="message",
            ),
        ],
        grouping_config=GroupingConfig(subdirectories=["subdir1", "subdir2"]),
    )
    assert len(groups) == 1
    assert len(groups[0].flags) == 2
    assert groups[0].flags[0].filepath == "subdir1/file1.py"
    assert groups[0].flags[1].filepath == "subdir2/file1.py"


@pytest.mark.asyncio
async def test_find_flag_groups_with_group_by(executor: SandboxExecutor):
    groups = await executor.find_flag_groups(
        code_flags=[
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir1/file1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir2/file1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir3/file1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir1/file1.py")),
                message="message",
            ),
        ],
        grouping_config=GroupingConfig(group_by=GroupBy.FILE),
    )
    assert len(groups) == 3
    assert groups[0].segment == "subdir1/file1.py"
    assert groups[1].segment == "subdir2/file1.py"
    assert groups[2].segment == "subdir3/file1.py"

    assert len(groups[0].flags) == 2
    assert len(groups[1].flags) == 1
    assert len(groups[2].flags) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("codebase", [121], indirect=True)
async def test_find_flag_groups_with_group_by_app(executor: SandboxExecutor):
    groups = await executor.find_flag_groups(
        code_flags=[
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="a/b/app1/test1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="a/b/app2/test1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="a/b/app3/test1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="a/b/app2/test2.py")),
                message="message",
            ),
        ],
        grouping_config=GroupingConfig(group_by=GroupBy.APP),
    )
    count_by_segment = {group.segment: len(group.flags) for group in groups}
    assert count_by_segment == {"a/b/app1": 1, "a/b/app2": 2, "a/b/app3": 1}


@pytest.mark.skip(reason="TODO: add max_prs as part of find_flag_groups")
@pytest.mark.asyncio
async def test_find_flag_groups_with_max_prs(executor: SandboxExecutor):
    groups = await executor.find_flag_groups(
        code_flags=[
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir1/file1.py")),
                message="message",
            ),
            CodeFlag(
                symbol=MagicMock(file=MagicMock(filepath="subdir2/file1.py")),
                message="message",
            ),
        ],
        grouping_config=GroupingConfig(group_by=GroupBy.FILE, max_prs=0),
    )
    assert len(groups) == 0
