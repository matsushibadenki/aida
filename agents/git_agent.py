# path: aida/agents/git_agent.py
# title: Git Agent
# role: Executes Git commands within the project's sandbox environment.

import subprocess
from pathlib import Path

class GitAgent:
    """
    This agent is responsible for executing Git commands
    within a specified project directory.
    """
    def __init__(self):
        """
        Initializes the GitAgent.
        """
        pass

    def run(self, project_path: str, command: str) -> tuple[bool, str]:
        """
        Runs a Git command in the specified project path.

        Args:
            project_path: The absolute path to the project directory (sandbox).
            command: The Git command string to execute (e.g., "add .", "commit -m 'Initial commit'").

        Returns:
            A tuple containing a boolean indicating if the command succeeded (exit code 0),
            and a string with the captured output (stdout and stderr).
        """
        print(f"[GitAgent] Running command in '{project_path}': git {command}")

        if not Path(project_path).is_dir():
            return False, f"Error: Project path does not exist or is not a directory: {project_path}"

        try:
            # Construct the full command
            full_command = f"git {command}"
            
            # Execute the command
            process = subprocess.run(
                full_command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )

            output = f"--- STDOUT ---\n{process.stdout}\n\n--- STDERR ---\n{process.stderr}"

            if process.returncode == 0:
                print(f"[GitAgent] Git command executed successfully.")
                return True, output
            else:
                print(f"[GitAgent] Git command failed (exit code: {process.returncode}).")
                return False, output

        except subprocess.TimeoutExpired:
            return False, "Error: Git command execution timed out after 120 seconds."
        except Exception as e:
            return False, f"An unexpected error occurred while running the Git command: {e}"