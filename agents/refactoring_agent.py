# path: aida/agents/refactoring_agent.py
# title: Refactoring Agent
# role: Analyzes and refactors code to improve its quality.

from pathlib import Path
from typing import List
from aida.agents.base_agent import BaseAgent
from aida.schemas import CodeChange, ProjectMetadata, CodeChanges
from aida.llm_client import LLMClient
from aida.utils import clean_code

PROMPT_TEMPLATE = """
You are an expert software engineer specializing in code refactoring. Your task is to analyze the provided source code and refactor it to improve readability, maintainability, and performance without changing its external behavior.

**File to Refactor:**
`{file_path}`

**File Contents:**
```python
{file_content}
```

**Project File Structure (for context):**
{file_list}

**Your Task:**
1.  **Analyze the Code**: Carefully read the provided file content.
2.  **Identify Refactoring Opportunities**: Look for complex logic, long methods, unclear variable names, code duplication, or inefficient patterns.
3.  **Generate Refactored Code**: Rewrite the code to address the issues you identified. Ensure the public API (function names, parameters, return values) remains unchanged.
4.  **Format the Output**: Provide the complete refactored code for the file in a structured JSON format.

**Output Format:**
Respond with a JSON object that strictly adheres to the `CodeChanges` schema. The root object must have a "changes" key containing a list with a single `CodeChange` object for the refactored file.
{{
    "changes": [
        {{
            "file_path": "{file_path}",
            "action": "update",
            "content": "the full, refactored content of the file"
        }}
    ]
}}
If no refactoring is necessary, return an empty list: `{{"changes": []}}`.
"""

class RefactoringAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client)

    def run(
        self,
        file_path_str: str,
        sandbox_path: str,
        metadata: ProjectMetadata,
    ) -> list[CodeChange]:
        print(f"[RefactoringAgent] Analyzing '{file_path_str}' for refactoring opportunities...")
        
        target_file = Path(sandbox_path) / file_path_str
        if not target_file.is_file():
            print(f"[RefactoringAgent] Error: File not found at {target_file}")
            return []

        try:
            content = target_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"[RefactoringAgent] Error reading file {target_file}: {e}")
            return []

        prompt = PROMPT_TEMPLATE.format(
            file_path=file_path_str,
            file_content=content,
            file_list="\n".join(metadata.files),
        )
        
        response_model = self.llm_client.generate_json(prompt, output_schema=CodeChanges)
        
        if not response_model or not response_model.changes:
            print("[RefactoringAgent] No refactoring suggestions were generated.")
            return []

        for change in response_model.changes:
            if hasattr(change, 'content') and change.content:
                change.content = clean_code(change.content)
        
        print(f"[RefactoringAgent] Refactoring suggestions generated for '{file_path_str}'.")
        return response_model.changes
