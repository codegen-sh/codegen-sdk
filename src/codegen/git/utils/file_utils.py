import os


def create_file(file_path: str, content: str | bytes) -> str:
    # Define the file path, name, and content
    filepath = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    content = content

    # Call the create_file function
    os.makedirs(filepath, exist_ok=True)

    # Create the full file path by joining the directory and filename
    file_path = os.path.join(filepath, filename)

    # Write the content to the file
    if isinstance(content, str):
        with open(file_path, "w") as file:
            file.write(content)
    elif isinstance(content, bytes):
        with open(file_path, "wb") as file:
            file.write(content)
    else:
        msg = f"Invalid content type: {type(content)}"
        raise ValueError(msg)

    # Check if the file was created
    file_path = os.path.join(filepath, filename)
    if not os.path.exists(file_path):
        msg = f"Failed to create file {format(file_path)}"
        raise FileNotFoundError(msg)
    return file_path


def create_files(base_dir: str, files: dict[str, str]) -> None:
    for filename, content in files.items():
        create_file(os.path.join(base_dir, filename), content)
