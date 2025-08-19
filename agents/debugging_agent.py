# path: aida/agents/debugging_agent.py
# title: Debugging Agent
# role: Analyzes test failures and generates code fixes.

from typing import List
from pathlib import Path
from aida.agents.base_agent import BaseAgent
from aida.schemas import CodeChange, ProjectMetadata, CodeChanges
from aida.llm_client import LLMClient
from aida.rag import RetrievalAgent
from aida.utils import clean_code

PROMPT_TEMPLATE = """
You are an expert AI software engineer specializing in debugging. Your task is to analyze the provided test results, identify the root cause of the failure, and generate a code fix in a structured JSON format.

**User's Goal:**
"{goal}"

**Project File Structure:**
{file_list}

**Failed Test Output:**
<test_output>
{test_output}
</test_output>

**File Contents:**
<file_contents>
{file_contents}
</file_contents>

**Your Analysis & Task:**
1.  **Analyze the Failure**: Carefully read the `<test_output>`. Identify the exact error message, the failing test function, and the file and line number where the error occurred.
2.  **Identify Root Cause**: Based on the error, examine the relevant file contents in `<file_contents>`. The bug could be in the test code itself (e.g., incorrect assertion) or in the source code it's testing.
3.  **Generate a Fix**: Create a JSON object containing a list of `CodeChange` objects to fix the bug. You may need to modify one or more files. Ensure your fix is precise and directly addresses the root cause. Do not introduce new features.

**Output Format:**
Respond with a JSON object that strictly adheres to the `CodeChanges` schema. The root object must have a "changes" key containing a list of `CodeChange` objects. A `CodeChange` object has the following format:
{{
    "file_path": "path/to/file.py",
    "action": "create" | "update" | "delete",
    "content": "the full content of the file for create/update, or empty for delete"
}}
If you cannot find a fix, return an empty list: `{{"changes": []}}`.
"""

class DebuggingAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, retrieval_agent: RetrievalAgent):
        super().__init__(llm_client)
        self.retrieval_agent = retrieval_agent

    def run(
        self,
        goal: str,
        sandbox_path: str,
        test_output: str,
        metadata: ProjectMetadata,
    ) -> list[CodeChange] | None:
        print("[DebuggingAgent] Analyzing test failures to generate a fix...")
        
        file_contents = ""
        # 修正：関連性の高いファイルのみをコンテキストに含めるように変更
        relevant_files = self._find_relevant_files(test_output, metadata.files)

        for file_path_str in relevant_files:
            try:
                full_path = Path(sandbox_path) / file_path_str
                with full_path.open('r', encoding='utf-8') as f:
                    content = f.read()
                file_contents += f"\n--- {file_path_str} ---\n{content}\n"
            except (IOError, UnicodeDecodeError):
                continue

        prompt = PROMPT_TEMPLATE.format(
            goal=goal,
            file_list="\n".join(metadata.files),
            test_output=test_output,
            file_contents=file_contents,
        )
        
        response_model = self.llm_client.generate_json(prompt, output_schema=CodeChanges)
        
        if not response_model or not response_model.changes:
            print("[DebuggingAgent] Could not generate a fix.")
            return None

        response = response_model.changes
        for change in response:
            if hasattr(change, 'content') and change.content:
                change.content = clean_code(change.content)
        
        print("[DebuggingAgent] Potential code fix generated.")
        return response

    def _find_relevant_files(self, test_output: str, all_files: List[str]) -> List[str]:
        """
        Parses the test output to find file paths mentioned in tracebacks.
        """
        import re
        # A simple regex to find file paths in Python tracebacks
        # Example: File "/path/to/your/project/aida/workspace/test_app.py", line 5, in test_hello
        file_path_pattern = re.compile(r'File "([^"]+)", line \d+')
        
        mentioned_files = set(file_path_pattern.findall(test_output))
        
        # We need to find the relative path from the project root
        relevant_files = set()
        for path in mentioned_files:
            for project_file in all_files:
                if path.endswith(project_file):
                    relevant_files.add(project_file)
        
        # If no files are found in the traceback (e.g., no tests collected),
        # we might want to return all files as a fallback.
        if not relevant_files:
            return all_files
            
        return list(relevant_files)