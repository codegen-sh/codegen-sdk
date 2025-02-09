"""Tool for making semantic edits to files using a small, fast LLM."""

import difflib

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from codegen import Codebase


def extract_code_blocks(edit_spec: str) -> list[tuple[str, str]]:
    """Extract code blocks and their surrounding context from the edit specification.

    Args:
        edit_spec: The edit specification containing code blocks with "# ... existing code ..." markers

    Returns:
        List of tuples containing (before_context, code_block)
    """
    # Split on the special comment marker
    parts = edit_spec.split("# ... existing code ...")

    blocks = []
    for i in range(1, len(parts) - 1):  # Skip first and last which are just context
        before = parts[i - 1].strip()
        code = parts[i].strip()
        blocks.append((before, code))

    return blocks


def clean_llm_response(response: str) -> str:
    """Clean the LLM response by removing any markdown code block markers.

    Args:
        response: The raw response from the LLM

    Returns:
        Cleaned code content
    """
    # Remove any leading/trailing whitespace
    content = response.strip()

    # Remove markdown code block markers if present
    if content.startswith("```"):
        # Find the language specifier if any (e.g., ```python)
        first_newline = content.find("\n")
        if first_newline != -1:
            content = content[first_newline + 1 :]
        else:
            content = content[3:]  # Just remove the backticks

    if content.endswith("```"):
        content = content[:-3]

    return content.strip()


def generate_diff(original: str, modified: str) -> str:
    """Generate a unified diff between two strings.

    Args:
        original: Original content
        modified: Modified content

    Returns:
        Unified diff as a string
    """
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile="original",
        tofile="modified",
        lineterm="",
    )

    return "".join(diff)


def semantic_edit(codebase: Codebase, filepath: str, edit_spec: str) -> dict[str, str]:
    """Edit a file using a semantic edit specification.

    The edit specification should contain code blocks showing the desired changes,
    with "# ... existing code ..." or "// ... unchanged code ..." etc. markers to indicate unchanged code.

    Args:
        codebase: The codebase to operate on
        filepath: Path to the file to edit
        edit_spec: The edit specification showing desired changes

    Returns:
        Dict containing:
            - filepath: Path to the edited file
            - content: New content of the file
            - diff: Unified diff showing the changes
            - status: Success status

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the edit specification is invalid
    """
    try:
        file = codebase.get_file(filepath)
    except ValueError:
        msg = f"File not found: {filepath}"
        raise FileNotFoundError(msg)

    # Extract the code blocks and their context
    blocks = extract_code_blocks(edit_spec)
    if not blocks:
        msg = "Invalid edit specification - must contain at least one code block between '# ... existing code ...' markers"
        raise ValueError(msg)

    # Get the original content
    original_content = file.content

    # Create the messages for the LLM
    system_message = SystemMessage(
        content="""You are a code editing assistant that makes precise, minimal edits to code files.
IMPORTANT: Return ONLY the modified code content. Do not include any explanations, markdown formatting, or code block markers.
Your response should be exactly the code that should be in the file, nothing more and nothing less."""
    )

    human_message = HumanMessage(
        content=f"""Modify the given file content according to the edit specification.
The edit specification shows code blocks that should be changed, with markers for existing code.
Apply these changes carefully, preserving all code structure and formatting.

Original file content:
{original_content}

Edit specification:
{edit_spec}

Return ONLY the modified code content. Do not include any markdown formatting, explanations, or code block markers."""
    )

    # Call the LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=10000,
    )

    response = llm.invoke([system_message, human_message])
    modified_content = clean_llm_response(response.content)

    # Generate diff
    diff = generate_diff(original_content, modified_content)

    # Apply the edit
    file.edit(modified_content)
    codebase.commit()

    # Return the updated file state
    return {"filepath": filepath, "content": modified_content, "diff": diff, "status": "success"}
