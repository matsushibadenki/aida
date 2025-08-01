# path: aida/services/sandbox.py
# title: Sandbox Service
# role: Provides a sandboxed environment for code execution.

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Tuple

from .file_system import FileSystem

class Sandbox:
    """
    A service that provides an isolated environment for running code and tests.
    """
    def __init__(self, file_system: FileSystem):
        self._file_system = file_system
        self._sandbox_dir = Path("./.sandbox").resolve()
        self._setup()

    def _setup(self) -> None:
        """Sets up the sandbox directory."""
        if self._sandbox_dir.exists():
            shutil.rmtree(self._sandbox_dir)
        self._sandbox_dir.mkdir(parents=True, exist_ok=True)

    def run_command(self, command: list[str]) -> Tuple[bool, str]:
        """
        Runs a command inside the sandbox.

        Args:
            command: The command to run as a list of strings.

        Returns:
            A tuple containing a boolean success flag and the output string.
        """
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self._sandbox_dir,
                timeout=60,
            )
            output = process.stdout + process.stderr
            return process.returncode == 0, output
        except subprocess.TimeoutExpired:
            return False, "Error: Command execution timed out."
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"

    def run_pytest(self) -> Tuple[bool, str]:
        """Runs pytest inside the sandbox."""
        pytest_command = [sys.executable, "-m", "pytest", "."]
        return self.run_command(pytest_command)
        
    def get_path(self) -> Path:
        """Returns the path to the sandbox directory."""
        return self._sandbox_dir

    def cleanup(self) -> None:
        """Removes the sandbox directory."""
        if self._sandbox_dir.exists():
            shutil.rmtree(self._sandbox_dir)

    def copy_to(self, src: str, dest: str) -> None:
        """Copies a file or directory into the sandbox."""
        src_path = Path(src)
        dest_path = self._sandbox_dir / dest
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if src_path.is_dir():
            shutil.copytree(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)