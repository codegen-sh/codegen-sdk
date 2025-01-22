import re


def normalize_string(git_diff_string):
    # Replace sequences of hexadecimal digits with a consistent placeholder
    pattern = r"^index\s+[0-9a-f]+\.+[0-9a-f]*\s*.*$"
    normalized_diff = re.sub(pattern, "<hex>", git_diff_string, flags=re.MULTILINE)
    return normalized_diff


def normalize_imports(content: str) -> str:
    """Alphabetically sorts lines which start with "import" so we can compare
    Two source code strings without caring if their imports are in the same order
    """
    # Split the content into lines
    lines = content.strip().split("\n")

    # Separate import lines and other lines
    import_lines = [line for line in lines if re.match(r"^\s*import\s", line)]
    other_lines = [line for line in lines if not re.match(r"^\s*import\s", line)]

    # Sort the import lines
    sorted_imports = sorted(import_lines)

    # Combine the sorted imports with the other lines
    normalized_content = "\n".join(sorted_imports + other_lines)

    return normalized_content
