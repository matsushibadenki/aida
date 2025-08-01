# path: aida/services/file_system.py
# title: FileSystem Service
# role: Handles all file system operations.

import os
from pathlib import Path
from typing import List

class FileSystem:
    """A service for interacting with the file system."""

    def read(self, path: str) -> str:
        """Reads the content of a file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found at {path}"
        except Exception as e:
            return f"An error occurred while reading the file: {e}"

    def write(self, path: str, content: str) -> None:
        """Writes content to a file, creating directories if they don't exist."""
        try:
            # ファイルパスからディレクトリ部分を取得
            dir_path = os.path.dirname(path)
            # ディレクトリが存在しない場合に作成
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            # エラー発生時にコンソールに出力
            print(f"An error occurred while writing to the file at {path}: {e}")

    def list_files(self, path: str) -> List[str]:
        """Lists all files in a directory recursively."""
        if not os.path.isdir(path):
            return ["Error: Provided path is not a directory."]
        
        filepaths: List[str] = []
        for root, _, files in os.walk(path):
            for file in files:
                filepaths.append(os.path.join(root, file))
        return filepaths