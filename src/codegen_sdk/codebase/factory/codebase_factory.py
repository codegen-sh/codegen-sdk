from graph_sitter.codebase.config import CodebaseConfig, ProjectConfig
from graph_sitter.core.codebase import (
    Codebase,
    CodebaseType,
)
from graph_sitter.enums import ProgrammingLanguage

from codegen_git.repo_operator.local_repo_operator import LocalRepoOperator
from codegen_git.schemas.repo_config import BaseRepoConfig


class CodebaseFactory:
    ####################################################################################################################
    # CREATE CODEBASE
    ####################################################################################################################

    @staticmethod
    def get_codebase_from_files(
        repo_path: str = "/tmp/codegen_run_on_str",
        files: dict[str, str] = {},
        bot_commit: bool = True,
        repo_config: BaseRepoConfig = BaseRepoConfig(),
        programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON,
        config: CodebaseConfig = CodebaseConfig(),
    ) -> CodebaseType:
        op = LocalRepoOperator.create_from_files(repo_path=repo_path, files=files, bot_commit=bot_commit, repo_config=repo_config)
        projects = [ProjectConfig(repo_operator=op, programming_language=programming_language)]
        return Codebase(projects=projects, config=config)
