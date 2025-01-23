import pytest

from graph_sitter.ai.helpers import count_tokens
from graph_sitter.code_generation.doc_utils.utils import get_decorator_for_language
from graph_sitter.code_generation.prompts.api_docs import get_graph_sitter_codebase, get_graph_sitter_docs
from graph_sitter.core.symbol import Symbol
from graph_sitter.enums import ProgrammingLanguage


@pytest.fixture(scope="module")
def codebase():
    return get_graph_sitter_codebase()


@pytest.mark.xdist_group("codegen")
def test_basic_docs(codebase) -> None:
    # =====[ Grab codebase ]=====
    language = ProgrammingLanguage.PYTHON
    api_docs = get_graph_sitter_docs(language=language, codebase=codebase)
    assert "class File" in api_docs
    assert "class PyFile" in api_docs
    assert "class Function" in api_docs
    assert "class PyFunction" in api_docs
    assert "class PyClass" in api_docs

    # =====[ Codebase class ]=====
    assert "class Codebase" in api_docs
    assert "def has_symbol" in api_docs
    assert "def create_file" in api_docs

    # =====[ "Behaviors" docstring ]====
    assert "class HasName" in api_docs
    assert "class HasValue" in api_docs


@pytest.mark.xdist_group("codegen")
@pytest.mark.parametrize("language", [ProgrammingLanguage.PYTHON, ProgrammingLanguage.TYPESCRIPT])
def test_api_doc_generation_sanity(codebase, language: ProgrammingLanguage) -> None:
    lang = "Py" if language == ProgrammingLanguage.PYTHON else "TS"
    other_lang = "TS" if language == ProgrammingLanguage.PYTHON else "Py"
    # =====[ Python ]=====
    docs = get_graph_sitter_docs(language=language, codebase=codebase)
    assert count_tokens(docs) < 50500
    assert f"{lang}Function" in docs
    assert f"{lang}Class" in docs
    assert f"{other_lang}Function" not in docs
    # assert "InviteFactoryCreateParams" in docs # Canonicals aren't in docs


@pytest.mark.xdist_group("codegen")
@pytest.mark.parametrize("language", [ProgrammingLanguage.PYTHON, ProgrammingLanguage.TYPESCRIPT])
def test_get_graph_sitter_codebase(codebase, language) -> None:
    """Make sure we can get the current codebase for GraphSitter, and that imports get resolved correctly"""
    cls = codebase.get_symbol("PyClass")
    assert cls is not None
    func = codebase.get_symbol("PyFunction")
    superclasses = func.superclasses()
    callable = [x for x in superclasses if isinstance(x, Symbol) and x.name == "Callable"]
    assert len(callable) == 1


@pytest.mark.xdist_group("codegen")
@pytest.mark.parametrize("language", [ProgrammingLanguage.PYTHON, ProgrammingLanguage.TYPESCRIPT])
def test_api_doc_generation(codebase, language) -> None:
    api_docs = get_graph_sitter_docs(language=language, codebase=codebase)
    decorator = get_decorator_for_language(language).value

    for cls in codebase.classes:
        if decorator in [decorator.name for decorator in cls.decorators]:
            assert f"class {cls.name}" in api_docs, f"Documentation for class '{cls.name}' not found in {language.value} API docs"
