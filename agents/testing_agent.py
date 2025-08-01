# path: aida/agents/testing_agent.py
# title: Testing Agent
# role: Executes tests using pytest and reports results.

import subprocess
import sys
from pathlib import Path

class TestingAgent:
    """
    This agent is responsible for running the test suite for the project.
    """
    def __init__(self):
        """
        Initializes the TestingAgent.
        """
        pass

    def run_tests(self, project_path: str) -> tuple[bool, str]:
        """
        Runs the test suite in the specified project path using pytest.

        Args:
            project_path: The absolute path to the project directory.

        Returns:
            A tuple containing a boolean indicating if tests passed,
            and a string with the captured output (stdout and stderr).
        """
        print(f"[TestingAgent] Running tests in: {project_path}")
        
        if not Path(project_path).is_dir():
            return False, f"Error: Project path does not exist or is not a directory: {project_path}"

        try:
            # Execute pytest, capturing both stdout and stderr for a full report.
            process = subprocess.run(
                [sys.executable, "-m", "pytest"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = f"--- STDOUT ---\n{process.stdout}\n\n--- STDERR ---\n{process.stderr}"

            if process.returncode == 0:
                print("[TestingAgent] All tests passed.")
                return True, output
            else:
                print(f"[TestingAgent] Some tests failed (exit code: {process.returncode}).")
                return False, output

        except FileNotFoundError:
            return False, "Error: 'pytest' command not found. Make sure pytest is installed."
        except subprocess.TimeoutExpired:
            return False, "Error: Tests timed out after 60 seconds."
        except Exception as e:
            return False, f"An unexpected error occurred while running tests: {e}"