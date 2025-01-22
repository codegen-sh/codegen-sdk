import os.path

from graph_sitter.code_generation.current_code_codebase import get_codegen_codebase_base_path, get_current_code_codebase
from graph_sitter.codebase.config import CodebaseConfig
from graph_sitter.core.codebase import Codebase


def get_graph_sitter_subdirectories() -> list[str]:
    base = get_codegen_codebase_base_path()
    return [os.path.join(base, "graph_sitter"), os.path.join(base, "codemods")]


def get_graph_sitter_codebase() -> Codebase:
    """Grabs a Codebase w/ GraphSitter content. Responsible for figuring out where it is, e.g. in Modal or local"""
    codebase = get_current_code_codebase(CodebaseConfig(), subdirectories=get_graph_sitter_subdirectories())
    return codebase
