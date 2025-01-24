from codegen.sdk.enums import ProgrammingLanguage


def canonical(codemod):
    """Decorator for canonical Codemods that will be used for AI-agent prompts."""
    codemod._canonical = True
    if not hasattr(codemod, "language") or codemod.language not in (ProgrammingLanguage.PYTHON, ProgrammingLanguage.TYPESCRIPT):
        raise AttributeError("Canonical codemods must have a `language` attribute (PYTHON or TYPESCRIPT).")
    return codemod
