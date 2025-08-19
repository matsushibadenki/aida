# path: aida/agents/dependency_agent.py
# title: Dependency Agent
# role: Manages project dependencies using pip.

import subprocess
import sys
from pathlib import Path

class DependencyAgent:
    """
    This agent is responsible for managing project dependencies using pip.
    """
    def __init__(self):
        """
        Initializes the DependencyAgent.
        """
        pass

    def run(self, project_path: str, command: str) -> tuple[bool, str]:
        """
        Runs a pip command in the specified project path.

        Args:
            project_path: The absolute path to the project directory (sandbox).
            command: The pip command string to execute (e.g., "install requests", "uninstall numpy").

        Returns:
            A tuple containing a boolean indicating if the command succeeded (exit code 0),
            and a string with the captured output (stdout and stderr).
        """
        print(f"[DependencyAgent] Running command in '{project_path}': pip {command}")

        if not Path(project_path).is_dir():
            return False, f"Error: Project path does not exist or is not a directory: {project_path}"

        try:
            # Use the same Python executable that is running the script
            # to ensure we're targeting the correct environment's pip.
            pip_command = [sys.executable, "-m", "pip"]
            full_command = pip_command + command.split()
            
            # Execute the command
            process = subprocess.run(
                full_command,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300 # Increased timeout for package installation
            )

            output = f"--- STDOUT ---\n{process.stdout}\n\n--- STDERR ---\n{process.stderr}"

            if process.returncode == 0:
                print(f"[DependencyAgent] Pip command executed successfully.")
                return True, output
            else:
                print(f"[DependencyAgent] Pip command failed (exit code: {process.returncode}).")
                return False, output

        except subprocess.TimeoutExpired:
            return False, "Error: Pip command execution timed out after 300 seconds."
        except Exception as e:
            return False, f"An unexpected error occurred while running the pip command: {e}"