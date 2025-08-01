# path: aida/agents/search_agent.py
# title: Search Agent
# role: Searches for files and their content within a directory.

import os
from typing import List

class SearchAgent:
    """
    An agent responsible for searching files within a directory,
    with an option to search inside file contents.
    """
    def __init__(self) -> None:
        # List of file extensions to consider as text files
        self.text_extensions = {
            '.py', '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css', '.js',
            '.ts', '.tsx', '.jsx', '.sh', '.toml', '.ini', '.cfg', '.xml', '.log'
        }
        # List of directories to ignore
        self.ignore_dirs = {
            '.git', '__pycache__', 'node_modules', 'dist', 'build', 'venv',
            '.vscode', '.idea'
        }

    def _is_text_file(self, file_path: str) -> bool:
        """Checks if a file is likely a text file based on its extension."""
        return os.path.splitext(file_path)[1] in self.text_extensions

    def run(self, directory: str, query: str = "") -> List[str]:
        """
        Searches for files in the given directory.

        Args:
            directory: The path to the directory to search.
            query: An optional query string to search for within file contents.
                   If empty, returns all text files.

        Returns:
            A list of file paths that match the criteria.
        """
        print(f"Searching in directory: {directory} for query: '{query}'")
        matched_files: List[str] = []
        if not os.path.isdir(directory):
            print(f"Error: Directory not found at {directory}")
            return matched_files

        for root, dirs, files in os.walk(directory):
            # Exclude ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            for file in files:
                file_path = os.path.join(root, file)
                if self._is_text_file(file_path):
                    if query:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                if query in f.read():
                                    matched_files.append(file_path)
                        except Exception as e:
                            print(f"Could not read file {file_path}: {e}")
                    else:
                        matched_files.append(file_path)
        return matched_files