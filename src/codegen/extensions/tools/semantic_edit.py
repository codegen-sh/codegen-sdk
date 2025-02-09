"""Tool for making semantic edits to files using a small, fast LLM."""

from typing import Any

import anthropic

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


def semantic_edit(codebase: Codebase, filepath: str, edit_spec: str) -> dict[str, Any]:
    """Edit a file using a semantic edit specification.

    The edit specification should contain code blocks showing the desired changes,
    with "# ... existing code ..." markers to indicate unchanged code.

    Args:
        codebase: The codebase to operate on
        filepath: Path to the file to edit
        edit_spec: The edit specification showing desired changes

    Returns:
        Dict containing the updated file state

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

    # Create the prompt for the LLM
    prompt = f"""You are a code editing assistant. Your task is to modify the given file content according to the edit specification.
The edit specification shows code blocks that should be changed, with markers for existing code.
Please apply these changes carefully, preserving all code structure and formatting.

Original file content:
```
{original_content}
```

Edit specification:
```
{edit_spec}
```

Return ONLY the modified file content, exactly as it should appear after the changes."""

    # Call Claude Haiku to make the edit
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        temperature=0,
        system="You are a code editing assistant. You make precise, minimal edits to code files based on edit specifications. Return ONLY the modified code, no explanations.",
        messages=[{"role": "user", "content": prompt}],
    )

    # Get the modified content
    modified_content = message.content[0].text

    # Apply the edit
    file.edit(modified_content)
    codebase.commit()

    # Return the updated file state
    return {"filepath": filepath, "content": modified_content, "status": "success"}
