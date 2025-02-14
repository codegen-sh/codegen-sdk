"""Quick PR review bot using Codegen and Modal."""

import os
from typing import Any, Dict

import modal
from codegen import Codebase
from codegen.sdk.enums import ProgrammingLanguage
from github import Github
from github.PullRequest import PullRequest

########################################################
# Core PR Review Logic
########################################################

def review_pr(pr: PullRequest, gh_token: str) -> str:
    """Review a PR using Codegen's capabilities."""
    # Initialize codebase for the PR's repository
    codebase = Codebase.from_repo(
        f"{pr.base.repo.full_name}",
        programming_language=ProgrammingLanguage.PYTHON,
        tmp_dir="/root"
    )

    # Get modified symbols in PR
    modified_symbols = codebase.get_modified_symbols_in_pr(pr.number)
    
    # Collect context about modified symbols and their dependencies
    context_symbols = set()
    for symbol in modified_symbols:
        # Get dependencies up to 2 levels deep
        deps = symbol.dependencies(max_depth=2)
        context_symbols.update(deps)
        
        # Get reverse dependencies up to 2 levels deep
        rev_deps = symbol.dependents(max_depth=2)
        context_symbols.update(rev_deps)

    # Prepare context for review
    review_context = {
        "pr_title": pr.title,
        "pr_body": pr.body,
        "modified_symbols": [
            {
                "name": symbol.name,
                "type": symbol.symbol_type.value,
                "filepath": symbol.filepath,
                "content": symbol.content,
            }
            for symbol in modified_symbols
        ],
        "context_symbols": [
            {
                "name": symbol.name,
                "type": symbol.symbol_type.value,
                "filepath": symbol.filepath,
            }
            for symbol in context_symbols
        ]
    }

    # Generate concise review using Codegen's AI capabilities
    system_prompt = """You are a helpful code reviewer. Provide concise, actionable feedback focusing on:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance implications
4. Security considerations

Keep reviews brief but informative. Use bullet points for clarity."""

    user_prompt = f"""Please review this PR:

Title: {review_context['pr_title']}
Description: {review_context['pr_body']}

Modified code and its dependencies are provided in the context.
Focus on the most important feedback that will improve code quality."""

    review = codebase.ai_client.llm_query_with_retry(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model="gpt-4",
        max_tokens=1000,
        temperature=0.3
    )

    return review

########################################################
# Modal Setup
########################################################

# Create image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install(
        "codegen>=0.6.1",
        "PyGithub>=2.1.1",
    )
)

# Create Modal app
app = modal.App("quick-pr-review")

@app.webhook(secret=modal.Secret.from_name("webhook-secret"))
def process_pr(payload: Dict[str, Any]):
    """Process PR webhook from GitHub."""
    # Only process PR events
    if "pull_request" not in payload:
        return {"status": "ignored", "reason": "not a PR event"}
        
    # Only process PR opened or synchronized events
    action = payload.get("action")
    if action not in ["opened", "synchronize"]:
        return {"status": "ignored", "reason": f"PR action {action} not handled"}

    try:
        # Initialize GitHub client
        gh = Github(os.environ["GITHUB_TOKEN"])
        repo = gh.get_repo(payload["repository"]["full_name"])
        pr = repo.get_pull(payload["pull_request"]["number"])
        
        # Generate review
        review = review_pr(pr, os.environ["GITHUB_TOKEN"])
        
        # Post review as comment
        pr.create_issue_comment(f"## Quick Code Review\n\n{review}")
        
        return {"status": "success", "message": "Review posted"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)} 