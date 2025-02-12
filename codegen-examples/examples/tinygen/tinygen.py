from typing import List, Tuple
from codegen import Codebase
from codegen.extensions.vector_index import VectorIndex
from codegen.extensions.langchain.agent import create_codebase_agent
from dotenv import load_dotenv

load_dotenv()


def setup_vector_search() -> VectorIndex:
    """Initialize and create/load vector index for semantic code search."""
    global codebase

    index = VectorIndex(codebase)

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
    index: VectorIndex, query: str, k: int = 20, min_similarity: float = 0.2
) -> List[Tuple[str, float, str]]:
    """Search and retrieve most similar code files with preview snippets."""

    results = index.similarity_search(query, k=k)
    relevant_files = []

    for filepath, similarity in results:
        if similarity < min_similarity:
            continue

        try:
            file = index.codebase.get_file(filepath)
            preview = file.content[:200].replace("\n", " ").strip()
            if len(file.content) > 200:
                preview += "..."

            relevant_files.append((filepath, similarity, preview))
        except Exception as e:
            print(f"Warning: Could not read file {filepath}: {e}")

    return relevant_files


def process_files_with_agent(
    codebase: Codebase,
    files_to_process: List[Tuple[str, float, str]],
    query: str,
    model_name: str = "gpt-4o-mini",
    temperature: float = 0,
) -> List[str]:
    """Process and modify code files using an AI agent based on user query."""

    print("\nInitializing AI agent...")
    agent = create_codebase_agent(
        codebase=codebase,
        model_name=model_name,
        temperature=temperature,
        verbose=True,
    )

    print("\nProcessing files with AI agent...")
    print("=" * 80)

    modifications_made = False
    all_diffs = []

    # Process each file
    for filepath, similarity, preview in files_to_process:
        if not codebase.has_file(filepath):
            print(f"⚠️ File not found: {filepath}")
            continue

        print(f"\nProcessing file: {filepath}")
        print(f"Similarity score: {similarity:.2f}")
        print(f"Preview: {preview[:100]}...")

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
            result = agent.invoke(
                input={"input": file_prompt},
                config={"configurable": {"session_id": filepath}},
            )

            print(f"✅ Processed {filepath}")
            print(f"Agent output: {result['output']}")
            print("-" * 80)
            modifications_made = True

        except Exception as e:
            print(f"❌ Error processing {filepath}: {str(e)}")
            print("-" * 80)

    if modifications_made:
        print("\nCommitting changes to disk...")
        try:
            codebase.commit()
            print("✅ Changes committed successfully")
        except Exception as e:
            print(f"❌ Error committing changes: {str(e)}")
    else:
        print("\nℹ️ No changes were made to commit")

    return all_diffs


def main():
    """Entry point that handles repository setup, search, and code modifications."""
    repo = input("Enter GitHub repository (format: owner/repo): ")
    query = input("Enter your query or instruction: ")

    global codebase
    print(f"🔄 Initializing codebase for {repo}...")
    codebase = Codebase.from_repo(repo)

    index = setup_vector_search()

    print("\nSearching for relevant files...")
    results = find_relevant_files(index, query)

    print("\nMost relevant files:")
    print("-" * 80)
    for filepath, similarity, preview in results:
        print(f"\n📄 {filepath}")
        print(f"Similarity: {similarity:.2f}")
        print(f"Preview: {preview}")
        print("-" * 80)

    original_contents = {}
    for filepath, _, _ in results:
        if index.codebase.has_file(filepath):
            original_contents[filepath] = index.codebase.get_file(filepath).content

    all_diffs = process_files_with_agent(index.codebase, results, query)

    print("\nAll Generated Diffs:")
    print("=" * 80)
    for diff in all_diffs:
        print(diff)
        print("-" * 80)

    #print("\nCreating PR...")
    #pr = codebase.create_pr(title="TinyGen PR", body="This PR was created by TinyGen")
    #print(f"Created PR: {pr.html_url}")

if __name__ == "__main__":
    main()
