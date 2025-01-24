import os
import sys
from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from typing import Any, Literal, overload

from codegen.git.repo_operator.local_repo_operator import LocalRepoOperator
from codegen.git.schemas.repo_config import BaseRepoConfig
from codegen.sdk.codebase.codebase_graph import CodebaseGraph
from codegen.sdk.codebase.config import CodebaseConfig, GSFeatureFlags, ProjectConfig, SessionOptions, TestFlags
from codegen.sdk.codebase.factory.codebase_factory import CodebaseFactory
from codegen.sdk.core.codebase import Codebase, PyCodebaseType, TSCodebaseType
from codegen.sdk.enums import ProgrammingLanguage
from codegen.sdk.secrets import Secrets
from codegen.sdk.tree_sitter_parser import print_errors


@overload
def get_codebase_session(
    tmpdir: str | os.PathLike[str],
    programming_language: Literal[ProgrammingLanguage.PYTHON],
    files: dict[str, str] = {},
    commit: bool = True,
    sync_graph: bool = True,
    verify_input: bool = True,
    verify_output: bool = True,
    repo_config: BaseRepoConfig | None = None,
    feature_flags: GSFeatureFlags = TestFlags,
    session_options: SessionOptions = SessionOptions(),
    secrets: Secrets = Secrets(),
) -> AbstractContextManager[PyCodebaseType]: ...


@overload
def get_codebase_session(
    tmpdir: str | os.PathLike[str],
    programming_language: Literal[ProgrammingLanguage.TYPESCRIPT],
    files: dict[str, str] = {},
    commit: bool = True,
    sync_graph: bool = True,
    verify_input: bool = True,
    verify_output: bool = True,
    repo_config: BaseRepoConfig | None = None,
    feature_flags: GSFeatureFlags = TestFlags,
    session_options: SessionOptions = SessionOptions(),
    secrets: Secrets = Secrets(),
) -> AbstractContextManager[TSCodebaseType]: ...


@contextmanager
def get_codebase_session(
    tmpdir: Any,
    programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON,
    files: dict[str, str] = {},
    commit: bool = True,
    sync_graph: bool = True,
    verify_input: bool = True,
    verify_output: bool = True,
    repo_config: BaseRepoConfig = BaseRepoConfig(),
    feature_flags: GSFeatureFlags = TestFlags,
    session_options: SessionOptions = SessionOptions(),
    secrets: Secrets = Secrets(),
) -> Generator[Codebase, None, None]:
    """Gives you a Codebase operating on the files you provided as a dict"""
    config = CodebaseConfig(feature_flags=feature_flags, secrets=secrets)
    codebase = CodebaseFactory.get_codebase_from_files(repo_path=str(tmpdir), files=files, config=config, programming_language=programming_language, repo_config=repo_config)
    with codebase.session(
        commit=commit,
        sync_graph=sync_graph,
        session_options=session_options,
    ):
        if verify_input:
            for file in codebase.files:
                if os.path.exists(file.filepath):
                    print_errors(file.filepath, file.content)
                    assert not file.ts_node.has_error, "Invalid syntax in test case"
        yield codebase

    if verify_output:
        for file in codebase.files:
            if os.path.exists(file.filepath):
                if file.ts_node.has_error and len(file.content.splitlines()) < 10:
                    print(file.content, file=sys.stderr)
                print_errors(file.filepath, file.content)
                assert not file.ts_node.has_error, "Invalid syntax in file after commiting"


@contextmanager
def get_codebase_graph_session(
    tmpdir: str,
    programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON,
    files: dict[str, str] = {},
    sync_graph: bool = True,
    session_options: SessionOptions = SessionOptions(),
) -> Generator[CodebaseGraph, None, None]:
    """Gives you a Codebase2 operating on the files you provided as a dict"""
    op = LocalRepoOperator.create_from_files(repo_path=tmpdir, files=files)
    config = CodebaseConfig(feature_flags=TestFlags)
    projects = [ProjectConfig(repo_operator=op, programming_language=programming_language)]
    graph = CodebaseGraph(projects=projects, config=config)
    with graph.session(sync_graph=sync_graph, session_options=session_options):
        try:
            yield graph
        finally:
            pass
