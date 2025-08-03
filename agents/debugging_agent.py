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
You are an expert AI software engineer specializing in debugging. Your task is to analyze the provided test results, identify the root cause of the failure, and generate a code fix.

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
2.  **Identify Root Cause**: Based on the error, examine the relevant file contents in `<file_contents>`. The bug could be in the test code itself (e.g., incorrect assertion, syntax error) or in the source code it's testing.
3.  **Generate a Fix**: Create a list of `CodeChange` objects to fix the bug. You may need to modify one or more files. Ensure your fix is precise and directly addresses the root cause. Do not introduce new features.

**Output Format:**
Respond with a JSON object that strictly adheres to the `CodeChanges` schema. The root object must have a "changes" key containing a list of `CodeChange` objects. If you cannot find a fix, return an empty list.
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
        for file_path_str in metadata.files:
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