# path: aida/agents/linting_agent.py
# title: Linting Agent
# role: Runs a linter to check code quality.

import subprocess
import sys
from pathlib import Path

class LintingAgent:
    """
    This agent is responsible for running a linter (flake8)
    on the project to check for style and quality issues.
    """
    def __init__(self):
        """
        Initializes the LintingAgent.
        """
        pass

    def run(self, project_path: str) -> tuple[bool, str]:
        """
        Runs flake8 on the specified project path.

        Args:
            project_path: The absolute path to the project directory (sandbox).

        Returns:
            A tuple containing a boolean indicating if linting passed (no issues found),
            and a string with the captured output.
        """
        print(f"[LintingAgent] Running linter in: {project_path}")

        if not Path(project_path).is_dir():
            return False, f"Error: Project path does not exist or is not a directory: {project_path}"

        try:
            # Command to run flake8
            command = [sys.executable, "-m", "flake8", "."]

            process = subprocess.run(
                command,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = f"--- Linter Output ---\n{process.stdout}\n{process.stderr}"

            # flake8 returns a non-zero exit code if issues are found.
            # We consider an empty stdout as success.
            if process.returncode == 0 or not process.stdout.strip():
                print("[LintingAgent] Linting passed. No issues found.")
                return True, "Linting passed. No issues found."
            else:
                print(f"[LintingAgent] Linting issues found.")
                return False, output

        except FileNotFoundError:
            # This case is unlikely if flake8 is in requirements.txt
            return False, "Error: 'flake8' command not found. Make sure flake8 is installed in the environment."
        except subprocess.TimeoutExpired:
            return False, "Error: Linter timed out after 60 seconds."
        except Exception as e:
            return False, f"An unexpected error occurred while running the linter: {e}"
