"""Vector index for semantic search over codebase files."""

import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import tiktoken
from openai import OpenAI
from tqdm import tqdm

from codegen import Codebase


class VectorIndex:
    """A vector index for semantic search over codebase files.

    This class manages embeddings for all files in a codebase, allowing for semantic search
    and similarity comparisons. It uses OpenAI's text-embedding model to generate embeddings
    and stores them efficiently on disk.

    Attributes:
        codebase (Codebase): The codebase to index
        E (Optional[np.ndarray]): The embeddings matrix, shape (n_files, embedding_dim)
        file_paths (Optional[np.ndarray]): Array of file paths corresponding to embeddings
    """

    DEFAULT_SAVE_DIR = ".codegen"
    DEFAULT_SAVE_FILE = "vector_index.pkl"
    EMBEDDING_MODEL = "text-embedding-3-small"
    MAX_TOKENS = 8000
    BATCH_SIZE = 100

    def __init__(self, codebase: Codebase):
        """Initialize the vector index.

        Args:
            codebase: The codebase to create embeddings for
        """
        self.codebase = codebase
        self.E: Optional[np.ndarray] = None
        self.file_paths: Optional[np.ndarray] = None

        # Initialize OpenAI client and tokenizer
        self.client = OpenAI()
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def _get_default_save_path(self) -> Path:
        """Get the default save path for the vector index."""
        save_dir = Path(self.codebase.repo_path) / self.DEFAULT_SAVE_DIR
        save_dir.mkdir(exist_ok=True)
        return save_dir / self.DEFAULT_SAVE_FILE

    def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for a batch of texts using OpenAI's API."""
        # Clean texts
        texts = [text.replace("\\n", " ") for text in texts]

        response = self.client.embeddings.create(model=self.EMBEDDING_MODEL, input=texts, encoding_format="float")
        return [data.embedding for data in response.data]

    def _split_by_tokens(self, text: str) -> list[str]:
        """Split text into chunks that fit within token limit."""
        tokens = self.encoding.encode(text)
        chunks = []
        current_chunk = []
        current_size = 0

        for token in tokens:
            if current_size + 1 > self.MAX_TOKENS:
                chunks.append(self.encoding.decode(current_chunk))
                current_chunk = [token]
                current_size = 1
            else:
                current_chunk.append(token)
                current_size += 1

        if current_chunk:
            chunks.append(self.encoding.decode(current_chunk))

        return chunks

    def create(self) -> None:
        """Create embeddings for all files in the codebase.

        This method processes all files in the codebase, generates embeddings using
        OpenAI's API, and stores them in memory. The embeddings can then be saved
        to disk using save().
        """
        # Store file paths and their embeddings
        file_embeddings = {}

        # Collect all valid files and their chunks
        chunks_to_process = []
        for file in tqdm(self.codebase.files, desc="Collecting files"):
            content = file.content
            if not content:  # Skip empty files
                continue

            # Split content into chunks by token count
            content_chunks = self._split_by_tokens(content)

            if len(content_chunks) == 1:
                # If only one chunk, store as is
                chunks_to_process.append((file.filepath, content, 0))
            else:
                # If multiple chunks, store with chunk index
                for i, chunk in enumerate(content_chunks):
                    chunks_to_process.append((file.filepath, chunk, i))

        # Process in batches
        for i in tqdm(range(0, len(chunks_to_process), self.BATCH_SIZE), desc="Processing batches"):
            batch = chunks_to_process[i : i + self.BATCH_SIZE]
            filepaths, contents, chunk_indices = zip(*batch)

            try:
                # Get embeddings for the batch
                embeddings = self._get_embeddings(contents)

                # Store results
                for filepath, content, chunk_idx, embedding in zip(filepaths, contents, chunk_indices, embeddings):
                    key = filepath if chunk_idx == 0 else f"{filepath}#chunk{chunk_idx}"
                    file_embeddings[key] = {"embedding": embedding, "content": content, "size": len(content), "chunk_index": chunk_idx}
            except Exception as e:
                print(f"Error processing batch {i // self.BATCH_SIZE}: {e}")

        # Convert to numpy arrays
        embeddings_list = []
        file_paths = []

        for filepath, data in file_embeddings.items():
            embeddings_list.append(data["embedding"])
            file_paths.append(filepath)

        self.E = np.array(embeddings_list)
        self.file_paths = np.array(file_paths)

    def save(self, save_path: Optional[str] = None) -> None:
        """Save the vector index to disk.

        Args:
            save_path: Optional path to save the index to. If not provided,
                      saves to .codegen/vector_index.pkl in the repo root.
        """
        if self.E is None or self.file_paths is None:
            msg = "No embeddings to save. Call create() first."
            raise ValueError(msg)

        save_path = Path(save_path) if save_path else self._get_default_save_path()

        # Ensure parent directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "wb") as f:
            pickle.dump({"E": self.E, "file_paths": self.file_paths}, f)

    def load(self, load_path: Optional[str] = None) -> None:
        """Load a previously saved vector index from disk.

        Args:
            load_path: Optional path to load the index from. If not provided,
                      loads from .codegen/vector_index.pkl in the repo root.
        """
        load_path = Path(load_path) if load_path else self._get_default_save_path()

        if not load_path.exists():
            msg = f"No vector index found at {load_path}"
            raise FileNotFoundError(msg)

        with open(load_path, "rb") as f:
            data = pickle.load(f)
            # Handle both old and new format
            self.E = data.get("E", data.get("embeddings"))
            self.file_paths = data["file_paths"]

    def get_embeddings(self, texts: list[str]) -> np.ndarray:
        """Get embeddings for a list of texts using the same model as the index.

        Args:
            texts: List of text strings to get embeddings for

        Returns:
            np.ndarray: Array of embeddings with shape (len(texts), embedding_dim)
        """
        # Clean and get embeddings
        embeddings = self._get_embeddings(texts)
        return np.array(embeddings)

    def similarity_search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        """Find the k most similar files to a query text.

        Uses cosine similarity between the query embedding and all file embeddings
        to find the most similar files.

        Args:
            query: The text to search for
            k: Number of results to return (default: 5)

        Returns:
            List of tuples (filepath, similarity_score) sorted by similarity (highest first)

        Raises:
            ValueError: If the index hasn't been created yet (E is None)
        """
        if self.E is None or self.file_paths is None:
            msg = "No embeddings available. Call create() or load() first."
            raise ValueError(msg)

        # Get query embedding
        query_embedding = self.get_embeddings([query])[0]

        # Compute cosine similarity
        # Normalize vectors for cosine similarity
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        E_norm = self.E / np.linalg.norm(self.E, axis=1)[:, np.newaxis]
        similarities = np.dot(E_norm, query_norm)

        # Get top k indices
        top_indices = np.argsort(similarities)[-k:][::-1]

        # Return filepath and similarity score pairs
        results = []
        for idx in top_indices:
            results.append((self.file_paths[idx], float(similarities[idx])))

        return results
