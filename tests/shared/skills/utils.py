import importlib
from collections.abc import Callable
from pathlib import Path

from codegen.sdk.core.codebase import CodebaseType
from tests.shared.skills.skill import Skill
from tests.shared.skills.skill_implementation import SkillImplementation

ExecuteFuncType = Callable[[CodebaseType], None]

# This is a registry that holds all skill implementations
skill_name_to_skill_implementations: dict[str, list[SkillImplementation]] = {}
skills: list[Skill] = []
SkillDecoratorType = Callable[[ExecuteFuncType], SkillImplementation]
REPO_ROOT_PATH: Path = Path(__file__).parent.parent.parent.parent
SKILLS_PATH: Path = REPO_ROOT_PATH / "tests" / "unit" / "skills" / "implementations"
CODEMODS_PATH: Path = REPO_ROOT_PATH / "src" / "codemods" / "canonical"


def import_skills_from(path: Path, module_prefix: str) -> None:
    for file in path.rglob("*.py"):
        relative_path = file.relative_to(path)
        if "evaluation" in relative_path.parts or "__init__" in file.name:
            continue
        module = module_prefix + "." + str(relative_path).replace("/", ".").removesuffix(".py")
        importlib.import_module(module)


def import_all_skills() -> None:
    import_skills_from(SKILLS_PATH, "tests.unit.skills.implementations")
    import_skills_from(CODEMODS_PATH, "codemods.canonical")


def get_all_skill_implementations() -> list[SkillImplementation]:
    """Get all skills."""
    import_all_skills()
    all_skills = []
    for skill_list in skill_name_to_skill_implementations.values():
        all_skills.extend(skill_list)
    return all_skills
