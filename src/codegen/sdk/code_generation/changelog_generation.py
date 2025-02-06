import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from git import Repo
from semantic_release import ParsedCommit, ParseError
from semantic_release.changelog.release_history import Release, ReleaseHistory
from semantic_release.cli.cli_context import CliContextObj
from semantic_release.cli.config import GlobalCommandLineOptions

import codegen
from codegen.sdk.ai.helpers import AnthropicHelper

if TYPE_CHECKING:
    import anthropic

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
## Role
You are a Release Manager for an open source project and have a gift for gleaning the most important and relevant changes from a list of commits.

## Objective
You will be given a list of commits for a specifc release and you will need to write a high level summary of the changes in 1 to 5 bullet points and generate a very concise description of the release.
The description should be a maximum of 60 characters and should only highlight the most important change(s).
Please do not include specific details about pull requests or commits, only summarize the changes in the context of the release.

## Instructions
- Do not include specific details about pull requests or commits, only summarize the changes in the context of the release.
- Do not include any other text than the bullet points and the one sentence description of the release.f
- Do not include pull request links or numbers.
- Only include information that is relevant to users and contributors.
- The description should be a maximum of 60 characters.

## Output
- Output the bullet points and the one sentence description of the release, no other text. The output should be a json object with the following keys:
    - `bullet_points`: A list of bullet points
    - `description`: A one sentence description of the release

## Example Outputs
```
{
    "bullet_points": [
        "Add new feature X",
        "Fix bug Y",
        "Improve performance"
    ],
    "description": "adds a new feature, fixes a bug, and improves performance."
}
```

## Things to exclude
- Removed development package publishing to AWS
- Updated various dependencies and pre-commit hooks

## Poor Release Descriptions
- "This release includes platform support updates, file handling improvements, and module resolution adjustments."
- "This release adds ARM support for Linux, enhances documentation, and includes dependency updates."

## Better Release Descriptions
- "Platform support updates"
- "ARM support for Linux"
"""


@dataclass
class ContextMock:
    config_file = "/Users/jesusmeza/Documents/codegen-sdk/pyproject.toml"

    def get_parameter_source(self, param_name):
        if hasattr(self, param_name):
            return getattr(self, param_name)
        return None


def generate_release_summary_context(release: Release):
    release_summary_context = {"version": release["version"].tag_format, "date": release["tagged_date"].strftime("%B %d, %Y"), "commits": dict()}
    elements = release["elements"]
    for title, commits in elements.items():
        release_summary_context["commits"][title] = []
        for parsed_commit in commits:
            if isinstance(parsed_commit, ParsedCommit):
                release_summary_context["commits"][title].append(parsed_commit.descriptions[0])
            elif isinstance(parsed_commit, ParseError):
                release_summary_context["commits"][title].append(parsed_commit.message)
    return release_summary_context


def generate_release_summary(client: AnthropicHelper, release: Release):
    release_summary_context = generate_release_summary_context(release)
    response: anthropic.types.message.Message = client.llm_query_no_retry(
        system_prompt=SYSTEM_PROMPT,
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""
Here is some context on the release:

{json.dumps(release_summary_context)}

Please write a high level summary of the changes in 1 to 5 bullet points.
""",
            }
        ],
    )
    if not response.content:
        msg = "No response from Anthropic"
        raise Exception(msg)

    return json.loads(response.content[0].text)


def generate_changelog(client: AnthropicHelper, complete: bool = False):
    ctx = CliContextObj(ContextMock(), logger=logger, global_opts=GlobalCommandLineOptions())
    runtime = ctx.runtime_ctx
    translator = runtime.version_translator
    with Repo(Path(codegen.__file__).parents[2]) as codegen_sdk_repo:
        release_history = ReleaseHistory.from_git_history(
            repo=codegen_sdk_repo,
            translator=translator,
            commit_parser=runtime.commit_parser,
            exclude_commit_patterns=runtime.changelog_excluded_commit_patterns,
        )

    releases = []
    parsed_releases: list[Release] = release_history.released.values()
    parsed_releases = sorted(parsed_releases, key=lambda x: x["tagged_date"], reverse=True)
    for release in parsed_releases:
        version = f"v{release['version']!s}"
        tag_url = f"https://github.com/codegen-sh/codegen-sdk/releases/tag/{version}"
        release_summary = generate_release_summary(client, release)
        release_content = f"""
<Update label="{version}" description="{release["tagged_date"].strftime("%B %d, %Y")}">
### [{release_summary["description"]}]({tag_url})
- {"\n- ".join(release_summary["bullet_points"])}
</Update>
"""
        releases.append(release_content)
        if not complete:
            break

    return "\n".join(releases)
