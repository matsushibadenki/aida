# path: aida/rag/indexing_agent.py
# title: Indexing Agent
# role: Handles the process of splitting and storing file content in the vector database.

import os
from pathlib import Path
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .vector_store import VectorStore
from ..schemas import CodeChange

class IndexingAgent:
    """
    This agent is responsible for reading files, splitting them into chunks,
    and adding them to the vector store for later retrieval.
    It supports both full indexing and incremental updates.
    """
    def __init__(self, vector_store: VectorStore, chunk_size: int, chunk_overlap: int):
        self.vector_store = vector_store
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def run_full_index(self, project_root: str, file_paths: List[str]):
        """
        Performs a full indexing of all specified files.
        The cleanup of the old index is now handled by the main application startup.
        """
        print("[IndexingAgent] Running full index...")
        self._process_files(project_root, file_paths)
        print("[IndexingAgent] Full indexing complete.")

    def update_index(self, project_root: str, changes: List[CodeChange]):
        """
        Incrementally updates the index based on a list of code changes.
        """
        print(f"[IndexingAgent] Updating index with {len(changes)} change(s)...")
        for change in changes:
            if change.action in ["update", "delete"]:
                self.vector_store.delete(file_path=change.file_path)

            if change.action in ["create", "update"]:
                self._process_files(project_root, [change.file_path])
        print("[IndexingAgent] Index update complete.")

    def _process_files(self, project_root: str, file_paths: List[str]):
        """
        Helper method to process a list of files and add them to the vector store.
        """
        all_texts = []
        all_metadatas = []

        for file_path_str in file_paths:
            full_path = Path(project_root) / file_path_str
            if not full_path.is_file():
                continue

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                chunks = self.text_splitter.split_text(content)
                metadatas = [{"source": file_path_str} for _ in chunks]
                
                all_texts.extend(chunks)
                all_metadatas.extend(metadatas)
                
            except (UnicodeDecodeError, IOError):
                print(f"[IndexingAgent] Warning: Could not decode file {file_path_str} as utf-8, skipping.")
                continue

        if all_texts:
            self.vector_store.add(documents=all_texts, metadatas=all_metadatas)