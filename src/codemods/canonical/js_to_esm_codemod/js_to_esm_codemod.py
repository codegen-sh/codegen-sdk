from graph_sitter.codemod import Codemod3
from graph_sitter.core.codebase import Codebase
from graph_sitter.enums import ProgrammingLanguage
from graph_sitter.skills.core.skill import Skill
from graph_sitter.skills.core.utils import skill, skill_impl
from graph_sitter.writer_decorators import canonical


@skill(
    canonical=True,
    prompt="""Generate a Python function named `execute` within a class `JsToEsmCodemod` that iterates through all files in a given `codebase`. For each file, check
if its name contains '.router'. If it does, convert the file to ESM format and update its filename to have a '.ts' extension, preserving the original
directory structure.""",
    uid="f93122d3-f469-4740-a8bf-f53016de41b2",
)
@canonical
class JsToEsmCodemod(Codemod3, Skill):
    """This codemod will convert all JS files that have .router in their name to be proper ESM modules"""

    language = ProgrammingLanguage.TYPESCRIPT

    @skill_impl(test_cases=[], skip_test=True, language=ProgrammingLanguage.TYPESCRIPT)
    def execute(self, codebase: Codebase) -> None:
        # iterate all files in the codebase
        for file in codebase.files:
            # Check if the file is not a router file
            if ".router" in file.name:
                # Convert the file to ESM
                file.convert_js_to_esm()
                # Update filename
                new_file_dir = "/".join(file.filepath.split("/")[:-1])
                new_file_name = ".".join(file.name.split(".")[:3])
                file.update_filepath(f"{new_file_dir}/{new_file_name}.ts")
