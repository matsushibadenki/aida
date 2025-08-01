# path: aida/utils.py
# title: Utility Functions
# role: Provides helper functions used across the application.

import json
from contextlib import contextmanager
from typing import Generator
import shutil
from pathlib import Path

def clean_code(code_string: str) -> str:
    """
    Cleans up a string of code by removing markdown fences and leading/trailing whitespace.
    """
    if '```' in code_string:
        first_newline = code_string.find('\n', code_string.find('```'))
        last_fence = code_string.rfind('```')
        if first_newline != -1 and last_fence != -1:
            return code_string[first_newline + 1 : last_fence].strip()
    return code_string.strip() if isinstance(code_string, str) else ""

def clean_json_response(raw_response: str) -> str:
    """
    Extracts a JSON object or array from a raw string response from an LLM.
    """
    if "```json" in raw_response:
        start_index = raw_response.find("```json") + len("```json")
        end_index = raw_response.rfind("```")
        if end_index > start_index:
            raw_response = raw_response[start_index:end_index]

    start_brace = raw_response.find('{')
    start_bracket = raw_response.find('[')

    start_index = -1
    if start_brace == -1 and start_bracket == -1:
        return ""
    elif start_brace == -1:
        start_index = start_bracket
    elif start_bracket == -1:
        start_index = start_brace
    else:
        start_index = min(start_brace, start_bracket)

    end_brace = raw_response.rfind('}')
    end_bracket = raw_response.rfind(']')
    end_index = max(end_brace, end_bracket)

    if start_index != -1 and end_index != -1 and end_index > start_index:
        return raw_response[start_index:end_index + 1].strip()
    
    return ""

@contextmanager
def sandbox_manager(project_path: str) -> Generator[str, None, None]:
    """
    A context manager to create and clean up a sandbox environment for code execution.
    """
    aida_root = Path(__file__).parent
    # The sandbox path is now correctly located inside the 'aida' directory.
    sandbox_path = aida_root / "aida_sandbox"
    
    if sandbox_path.exists():
        shutil.rmtree(sandbox_path)
    
    shutil.copytree(project_path, sandbox_path, dirs_exist_ok=True)
    
    # Copy pytest.ini to the sandbox root. The original is in the project root (parent of aida).
    project_root_dir = aida_root.parent
    pytest_ini_path = project_root_dir / 'pytest.ini'
    if pytest_ini_path.exists():
        shutil.copy(pytest_ini_path, sandbox_path)

    try:
        yield str(sandbox_path)
    finally:
        # This cleanup is for after each task run.
        if sandbox_path.exists():
            shutil.rmtree(sandbox_path)