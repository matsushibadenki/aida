# path: aida/analysis/project_analyzer.py
# title: Project Analyzer
# role: Analyzes the file system of a given project directory.

import os
from pathlib import Path
from typing import List

class ProjectAnalyzer:
    """
    A utility class to analyze a project's directory structure.
    """
    def __init__(self, project_path: str):
        """
        Initializes the analyzer with the project's root path.

        Args:
            project_path: The absolute or relative path to the project's root directory.
        """
        self.project_root = Path(project_path).resolve()
        if not self.project_root.is_dir():
            raise NotADirectoryError(f"The provided path '{project_path}' is not a valid directory.")

    def list_files(self) -> List[str]:
        """
        Recursively lists all files within the project directory, returning their
        relative paths from the project root.

        It ignores common virtual environment and cache directories.

        Returns:
            A list of strings, where each string is a relative file path.
        """
        filepaths: List[str] = []
        ignore_dirs = {'.venv', '__pycache__', '.git', '.idea', '.vscode', '.DS_Store'}

        for root, dirs, files in os.walk(self.project_root, topdown=True):
            # topdown=True allows us to modify dirs in-place to prune the search
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                full_path = Path(root) / file
                relative_path = full_path.relative_to(self.project_root)
                filepaths.append(str(relative_path))
                
        return filepaths

    def get_project_root(self) -> Path:
        """
        Returns the resolved, absolute path of the project root.

        Returns:
            A Path object representing the project root directory.
        """
        return self.project_root