# TinyGen: AI-Powered Code Modification Tool

TinyGen is a tool that modifies codebases based on simple text prompts. It utilizes the Codegen package and agents to perform changes end-to-end.

## How TinyGen Works

The script (`tinygen.py`) processes code modifications in three key steps:

1. **Semantic Code Search**

   ```python
   index = setup_vector_search()
   results = find_relevant_files(index, query)
   ```

   - Creates embeddings for all files in the codebase
   - Uses vector similarity to find relevant code files
   - Filters results based on similarity threshold

2. **Intelligent File Selection**

   ```python
   for filepath, similarity, preview in results:
       print(f"📄 {filepath}")
       print(f"Similarity: {similarity:.2f}")
       print(f"Preview: {preview}")
   ```

   - Shows most relevant files with similarity scores
   - Provides content previews for context
   - Helps users understand what will be modified

3. **AI-Powered Modifications**

   ```python
   agent = create_codebase_agent(
       codebase=codebase,
       model_name=model_name,
       temperature=temperature,
       verbose=True
   )
   ```

   - Uses LangChain agents to analyze and modify code
   - Preserves code structure and functionality
   - Provides explanations for changes made

## Key Features

1. **Vector Search Integration**
   - Uses OpenAI embeddings for semantic code search
   - Caches embeddings for faster subsequent runs
   - Configurable similarity thresholds

2. **Smart File Processing**
   - Handles large codebases efficiently
   - Provides progress feedback
   - Maintains file integrity

3. **AI Agent Integration**
   - Contextual code modifications
   - Clear explanation of changes
   - Safety checks and validations

## Environment Setup

Add your OpenAI API key to the `.env` file:
```bash
OPENAI_API_KEY=your-api-key-here
```

You can get an API key from the [OpenAI platform](https://platform.openai.com/api-keys).

## Running TinyGen

```python
# Install dependencies
pip install codegen python-dotenv

# Run the script
python3 tinygen.py
```

## Contributing

Feel free to submit issues and enhancement requests!
