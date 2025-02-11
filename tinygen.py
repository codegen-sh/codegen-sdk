from typing import List, Tuple
from codegen import Codebase
from codegen.extensions.vector_index import VectorIndex
from codegen.extensions.langchain.agent import Agent, create_codebase_agent
import shutil
import tempfile
import git
from dotenv import load_dotenv

load_dotenv()


def setup_vector_search(repo_path: str) -> VectorIndex:
    """Initialize and create vector index for a codebase."""
    # Initialize codebase
    codebase = Codebase(repo_path)

    # Create vector index
    index = VectorIndex(codebase)

    # Try to load existing index, create if not found
    try:
        index.load()
        print("✓ Loaded existing vector index")
    except FileNotFoundError:
        print("⚡ Creating new vector index...")
        index.create()
        index.save()
        print("✓ Created and saved vector index")

    return index


def find_relevant_files(
    index: VectorIndex, query: str, k: int = 10, min_similarity: float = 0.1
) -> List[Tuple[str, float, str]]:
    """Find most relevant files for a query with previews."""
    # Perform semantic search
    results = index.similarity_search(query, k=k)

    relevant_files = []
    for filepath, similarity in results:
        print(filepath, similarity)
        # Skip if similarity is too low
        if similarity < min_similarity:
            continue

        # Get file content preview
        try:
            file = index.codebase.get_file(filepath)
            preview = file.content[:200].replace("\n", " ").strip()
            if len(file.content) > 200:
                preview += "..."

            relevant_files.append((filepath, similarity, preview))
        except Exception as e:
            print(f"Warning: Could not read file {filepath}: {e}")

    return relevant_files


def clone_repo(repo_url: str) -> str:
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Cloning repository from {repo_url} to {temp_dir}")
        git.Repo.clone_from(repo_url, temp_dir)
    except git.exc.GitError as e:
        shutil.rmtree(temp_dir)
        raise ValueError(f"Failed to clone repository: {e}")
    return temp_dir


def process_files_with_agent(
    codebase: Codebase,
    files_to_process: List[Tuple[str, float, str]],
    query: str,
    model_name: str = "gpt-4",
    temperature: float = 0,
) -> None:
    """Process relevant files using the LangChain agent.

    Args:
        codebase: The codebase object containing the files
        files_to_process: List of tuples containing (filepath, similarity, preview)
        query: The original query/prompt describing the changes to make
        model_name: Name of the model to use
        temperature: Model temperature
    """
    # Create the agent with the codebase tools
    print("\nInitializing AI agent...")
    agent = create_codebase_agent(
        codebase=codebase,
        model_name=model_name,
        temperature=temperature,
        verbose=True  # Enable verbose mode to see agent's thought process
    )

    print("\nProcessing files with AI agent...")
    print("=" * 80)

    modifications_made = False

    # Process each file
    for filepath, similarity, preview in files_to_process:
        if not codebase.has_file(filepath):
            print(f"⚠️ File not found: {filepath}")
            continue

        print(f"\nProcessing file: {filepath}")
        print(f"Similarity score: {similarity:.2f}")
        print(f"Preview: {preview[:100]}...")

        # Create a specific prompt for this file
        file_prompt = f"""
Analyze and modify the file {filepath} based on this request: "{query}"

Follow these steps:
1. First use the view_file tool to see the current content
2. Analyze the changes needed based on the request
3. Use the edit_file tool to make the necessary modifications
4. Explain what changes were made and why

Guidelines:
- Preserve the overall structure and functionality
- Only make changes that align with the request
- Ensure code quality and consistency
"""

        try:
            # Invoke the agent with the file-specific prompt
            result = agent.invoke(
                {
                    "input": file_prompt,
                    "config": {"configurable": {"session_id": filepath}},
                }
            )

            print(f"✅ Processed {filepath}")
            print(f"Agent output: {result['output']}")
            print("-" * 80)
            modifications_made = True

        except Exception as e:
            print(f"❌ Error processing {filepath}: {str(e)}")
            print("-" * 80)

    # Only commit if changes were made
    if modifications_made:
        print("\nCommitting changes to disk...")
        try:
            codebase.commit()
            print("✅ Changes committed successfully")
        except Exception as e:
            print(f"❌ Error committing changes: {str(e)}")
    else:
        print("\nℹ️ No changes were made to commit")


def main():
    # Example usage
    repo_url = "https://github.com/Textualize/rich"
    query = "Delete dead code"

    repo_path = clone_repo(repo_url)

    # Setup vector search
    index = setup_vector_search(repo_path)

    # Find relevant files
    print("\nSearching for relevant files...")
    results = find_relevant_files(index, query)

    # Display results
    print("\nMost relevant files:")
    print("-" * 80)
    for filepath, similarity, preview in results:
        print(f"\n📄 {filepath}")
        print(f"Similarity: {similarity:.2f}")
        print(f"Preview: {preview}")
        print("-" * 80)

    # Store original file contents for diff
    original_contents = {}
    for filepath, _, _ in results:
        if index.codebase.has_file(filepath):
            original_contents[filepath] = index.codebase.get_file(filepath).content

    # Process files with AI agent
    process_files_with_agent(index.codebase, results, query)

    # Print diffs for modified files
    print("\nFile modifications:")
    print("=" * 80)
    for filepath in original_contents:
        if index.codebase.has_file(filepath):
            new_content = index.codebase.get_file(filepath).content
            if new_content != original_contents[filepath]:
                from difflib import unified_diff

                diff = unified_diff(
                    original_contents[filepath].splitlines(keepends=True),
                    new_content.splitlines(keepends=True),
                    fromfile=f"a/{filepath}",
                    tofile=f"b/{filepath}",
                )
                print(f"\nChanges in {filepath}:")
                print("".join(diff))
            else:
                print(f"\nNo changes made to {filepath}")


if __name__ == "__main__":
    main()
