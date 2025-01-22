import importlib
import inspect
from collections.abc import Callable
from pathlib import Path

import inflection

from graph_sitter.core.codebase import CodebaseType
from graph_sitter.enums import ProgrammingLanguage
from graph_sitter.skills.core.skill import Skill
from graph_sitter.skills.core.skill_implementation import SkillImplementation
from graph_sitter.skills.core.skill_test import SkillTestCase

ExecuteFuncType = Callable[[CodebaseType], None]

# This is a registry that holds all skill implementations
skill_name_to_skill_implementations: dict[str, list[SkillImplementation]] = {}
skills: list[Skill] = []
SkillDecoratorType = Callable[[ExecuteFuncType], SkillImplementation]
SKILLS_PATH: Path = Path(__file__).parent.parent
CODEMODS_PATH: Path = Path(__file__).parent.parent.parent.parent / "codemods" / "canonical"


def skill_impl(
    test_cases: list[SkillTestCase],
    language: ProgrammingLanguage = ProgrammingLanguage.PYTHON,
    eval_skill: bool = False,
    skip_test: bool = False,
    prompt: str | None = None,
    ignore: bool = False,
    si_id: int | None = None,
    from_app: bool = False,
    external: bool = False,
) -> Callable[[ExecuteFuncType], ExecuteFuncType]:
    """Decorator for Skill functions. Returns a Skill when you wrap a function with it."""

    def decorator(func: [ExecuteFuncType | type]) -> Callable[[CodebaseType], None]:
        if ignore:
            return func
        new_skill = SkillImplementation(
            test_cases=test_cases,
            skill_func=func,
            language=language,
            eval_skill=eval_skill,
            skip_test=skip_test,
            prompt=prompt,
            si_id=si_id,
            from_app=from_app,
            external=external,
        )

        # Set the language-specific implementation on the parent class
        if func is not None:
            qualname_as_array = func.__qualname__.split(".")
            if len(qualname_as_array) > 1:
                assert properly_named_function(name=func.__name__, language=language), skill_func_name_error(name=func.__name__, language=language)
                if language == ProgrammingLanguage.PYTHON:
                    if not hasattr(func, "python_skill_implementation"):
                        func.python_skill_implementation = new_skill
                elif language == ProgrammingLanguage.TYPESCRIPT:
                    if not hasattr(func, "typescript_skill_implementation"):
                        func.typescript_skill_implementation = new_skill
                return func

            elif inspect.isfunction(func):
                raise ValueError("Please structure your skill as a Class.")

            else:
                raise ValueError(f"Unsupported function type: {type(func)}")

    return decorator


def properly_named_function(name: str, language: ProgrammingLanguage):
    if language == ProgrammingLanguage.PYTHON:
        return name == "skill_func" or name == "python_skill_func" or name == "execute"
    elif language == ProgrammingLanguage.TYPESCRIPT:
        return name == "skill_func" or name == "typescript_skill_func" or name == "execute"
    else:
        return False


def skill_func_name_error(name: str, language: ProgrammingLanguage):
    if language == ProgrammingLanguage.PYTHON:
        return f"Function name must be 'skill_func', 'python_skill_func' or 'execute' for Python skills. Got {name}."
    elif language == ProgrammingLanguage.TYPESCRIPT:
        return f"Function name must be 'skill_func', 'typescript_skill_func' or 'execute' for TypeScript skills. Got {name}."
    else:
        return "Unsupported language."


def populate_skill_implementation(skill_imp: "SkillImplementation", sk: "Skill"):
    """Populate a SkillImplementation with the name and eval_skill attribute."""
    skill_imp.name = inflection.underscore(sk.__name__)
    skill_imp.eval_skill = sk.eval_skill
    skill_imp.guide_skill = sk.guide
    if skill_imp.prompt is None:
        if sk.prompt is None:
            raise ValueError(f"Prompt is not set for skill: {sk.__name__} ({skill_imp.language}). Prompt must be set in either skill or skill implementation.")
        else:
            skill_imp.prompt = sk.prompt
    if skill_imp.doc is None:
        if sk.doc is None:
            raise ValueError(f"Docstring is not set for skill: {sk.__name__} ({skill_imp.language}). Docstring must be set in either skill or skill implementation.")
        else:
            skill_imp.doc = sk.doc
    return skill_imp


def skill(uid: str, eval_skill: bool = False, prompt: str | None = None, s_id: int | None = None, guide: bool = False, canonical=True):
    """Decorator for Skill classes. Adds the class to the skills list."""

    def decorator(cls):
        cls.prompt = prompt
        cls.name = inflection.underscore(cls.__name__)
        cls.doc = cls.__doc__
        cls.eval_skill = eval_skill
        cls.id = s_id
        cls.guide = guide
        cls.canonical = canonical
        cls.uid = uid
        new_attributes = {}
        for name, method in cls.__dict__.items():
            if name not in ["python_skill_func", "typescript_skill_func", "skill_func", "execute"] or not callable(method):
                continue
            if hasattr(method, "__func__"):
                func = method.__func__
            else:
                func = method

            if hasattr(func, "python_skill_implementation"):
                skill_imp = func.python_skill_implementation
                new_attributes["python_skill_implementation"] = populate_skill_implementation(skill_imp, cls)
            if hasattr(func, "typescript_skill_implementation"):
                skill_imp = func.typescript_skill_implementation
                new_attributes["typescript_skill_implementation"] = populate_skill_implementation(skill_imp, cls)
        for name, value in new_attributes.items():
            setattr(cls, name, value)

        if cls.name not in skill_name_to_skill_implementations:
            skill_name_to_skill_implementations[cls.name] = cls.implementations()
            skills.append(cls)
        else:
            raise ValueError(f"Skill with name {cls.name} ({cls.__name__}) already exists. Please Rename the skill class.")
        return cls

    return decorator


def import_skills_from(path: Path, package: str):
    for file in path.rglob("*.py"):
        relative_path = file.relative_to(path)
        if "evaluation" in relative_path.parts or "__init__" in file.name:
            continue
        module_name = package + "." + str(relative_path).replace("/", ".").removesuffix(".py")
        importlib.import_module(module_name)


def import_all_skills():
    import_skills_from(SKILLS_PATH, "graph_sitter.skills")
    import_skills_from(CODEMODS_PATH, "codemods.canonical")


def import_all_guide_skill_files():
    # HACK: force import all skills
    for file in SKILLS_PATH.rglob("*.py"):
        relative_path = file.relative_to(SKILLS_PATH)
        if "evaluation" in relative_path.parts or "__init__" in file.name or "guides" not in relative_path.parts:
            continue
        module_name = "graph_sitter.skills." + str(relative_path).replace("/", ".").removesuffix(".py")
        importlib.import_module(module_name)


def get_all_skills() -> list[Skill]:
    import_all_skills()
    return skills


def get_skill_name_to_skill_implementations() -> dict[str, list[SkillImplementation]]:
    import_all_skills()
    return skill_name_to_skill_implementations


def get_guide_skills_dict() -> dict:
    import_all_guide_skill_files()
    skills_dict = {}
    for sk in skills:
        if not sk.guide:
            continue
        sk_inst = sk
        name = sk_inst.guide_path()
        if name in skills_dict:
            skills_dict[name].append(sk_inst)
        else:
            skills_dict[name] = [sk_inst]
    return skills_dict


def get_all_skill_implementations() -> list[SkillImplementation]:
    """Get all skills."""
    import_all_skills()
    all_skills = []
    for skill_list in skill_name_to_skill_implementations.values():
        all_skills.extend(skill_list)
    return all_skills


def get_all_evaluation_skills() -> list[SkillImplementation]:
    """Get all evaluation skills."""
    all_skills = get_all_skill_implementations()
    return [sk for sk in all_skills if sk.eval_skill]
