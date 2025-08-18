# path: aida/rag/vector_store.py
# title: Vector Store
# role: Manages the vector database for document storage and retrieval.

import chromadb
from chromadb.api.types import EmbeddingFunction, Metadata
from typing import List, Dict, Any
from pathlib import Path

class VectorStore:
    """
    This class manages the ChromaDB vector store.
    It now accepts a custom embedding function.
    """
    def __init__(self, db_path: str, embedding_function: EmbeddingFunction):
        """
        Initializes the VectorStore.

        Args:
            db_path: The path to the database directory.
            embedding_function: The function or object to use for generating embeddings.
        """
        db_directory = Path(db_path)
        self.client = chromadb.PersistentClient(path=str(db_directory))
        self.embedding_function = embedding_function
        self.collection = self.client.get_or_create_collection(
            name="aida_collection",
            embedding_function=self.embedding_function
        )

    def add(self, documents: List[str], metadatas: List[Metadata]):
        """
        Adds documents to the vector store.
        """
        ids = [f"id_{hash(doc)}_{i}" for i, doc in enumerate(documents)]
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def delete(self, file_path: str):
        """
        Deletes all chunks associated with a specific file path from the collection.
        """
        print(f"[VectorStore] Deleting entries for file: {file_path}")
        self.collection.delete(where={"source": file_path})

    def search(self, query: str, n_results: int = 5) -> List[str]:
        """
        Searches for relevant documents in the vector store.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        documents_list = results.get('documents')
        if documents_list:
            return documents_list[0]
        return []

    def clear(self):
        """
        Clears all entries from the vector store collection.
        """
        try:
            self.client.delete_collection(name="aida_collection")
            self.collection = self.client.get_or_create_collection(
                name="aida_collection",
                embedding_function=self.embedding_function
            )
        except Exception as e:
            print(f"Error clearing collection: {e}")