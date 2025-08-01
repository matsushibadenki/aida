# path: aida/rag/retrieval_agent.py
# title: Retrieval Agent
# role: Retrieves relevant context from the vector store based on a query.

from typing import List
from .vector_store import VectorStore

class RetrievalAgent:
    """
    This agent retrieves relevant document chunks from the vector store
    based on a given query.
    """
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def run(self, query: str, n_results: int = 5) -> List[str]:
        """
        Searches the vector store for relevant documents.
        """
        print(f"[RetrievalAgent] Searching for context related to: '{query}'")
        
        # VectorStoreのsearchメソッドを正しい引数で呼び出す
        results = self.vector_store.search(query=query, n_results=n_results)
        return results