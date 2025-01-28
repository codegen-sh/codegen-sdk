from dataclasses import dataclass
from pathlib import Path

from codegen.sdk.python import PyFile
from codegen.sdk.typescript.file import TSFile


@dataclass
class SkillTestCasePyFile:
    """Represents a Skill test case file."""

    input: str
    output: str = ""
    filepath: str = "test.py"
    unchanged: bool = False


@dataclass
class SkillTestCaseTSFile:
    """Represents a Skill test case file."""

    input: str
    output: str = ""
    filepath: str = "test.ts"
    unchanged: bool = False


@dataclass
class SkillTestCase:
    """Represents a Skill test case (input/output).

    Rendered in docs & prompt_builders and ran as part of tests
    """

    files: list[SkillTestCasePyFile | SkillTestCaseTSFile]
    name: str | None = None  # name the test case to make it easier to find + test a specific case
    filepath: str = ""
    sanity: bool = False  # sanity check: run the skill on the input and check if the output is the same
    graph: bool = False

    @classmethod
    def from_files(cls, files: list[SkillTestCasePyFile | SkillTestCaseTSFile]) -> "SkillTestCase":
        return cls(files=files)

    @classmethod
    def from_dir(cls, filepath: Path) -> "SkillTestCase":
        original_dir = filepath / "original"
        expected_dir = filepath / "expected"

        # Get all unique file paths relative to their respective directories
        original_files = set(f.relative_to(original_dir) for f in original_dir.glob("**/*.*"))
        expected_files = set(f.relative_to(expected_dir) for f in expected_dir.glob("**/*.*"))

        # Combine unique file paths
        all_files = original_files.union(expected_files)

        files = []
        for relative_path in all_files:
            input_content = cls._read_file(original_dir / relative_path)
            output_content = cls._read_file(expected_dir / relative_path)

            if relative_path.suffix in PyFile.get_extensions():
                files.append(SkillTestCasePyFile(input=input_content, output=output_content, filepath=str(relative_path)))
            elif relative_path.suffix in TSFile.get_extensions():
                files.append(SkillTestCaseTSFile(input=input_content, output=output_content, filepath=str(relative_path)))
            else:
                msg = f"Unsupported file extension: {relative_path.suffix} for file: {relative_path}"
                raise ValueError(msg)

        return cls(files=files, filepath=str(filepath))

    @staticmethod
    def _read_file(filepath: Path) -> str:
        try:
            with open(filepath) as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def to_input_dict(self):
        return {x.filepath: x.input for x in self.files}
