"""Tool for making semantic edits to files using a small, fast LLM."""

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


def semantic_edit(codebase: Codebase, filepath: str, edit_spec: str) -> dict[str, str]:
    """Edit a file using a semantic edit specification.

    The edit specification should contain code blocks showing the desired changes,
    with "# ... existing code ..." or "// ... unchanged code ..." etc. markers to indicate unchanged code.

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

    # Create the messages for the LLM
    system_message = SystemMessage(
        content="You are a code editing assistant. You make precise, minimal edits to code files based on edit specifications. Return ONLY the modified code, no explanations."
    )

    human_message = HumanMessage(
        content=f"""Modify the given file content according to the edit specification.
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
    )

    # Call GPT-4-Turbo to make the edit
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=10000,
    )

    response = llm.invoke([system_message, human_message])
    modified_content = response.content

    # Apply the edit
    file.edit(modified_content)
    codebase.commit()

    # Return the updated file state
    return {"filepath": filepath, "content": modified_content, "status": "success"}
