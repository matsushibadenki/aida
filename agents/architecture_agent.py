# path: aida/agents/architecture_agent.py
# title: Architecture Agent
# role: Designs the high-level architecture and file structure for a project.

from typing import List
from aida.agents.base_agent import BaseAgent
from aida.schemas import ProjectMetadata, ArchitecturePlan
from aida.llm_client import LLMClient

PROMPT_TEMPLATE = """
You are an expert AI software architect. Your task is to design the file structure for a new software project based on the user's request.

**User's Goal:**
"{goal}"

**Existing Project File Structure (for context):**
{file_list}

**Your Task:**
1.  **Analyze the Goal**: Understand the core requirements of the user's request.
2.  **Design the Architecture**: Propose a clear and logical file structure.
3.  **Describe Each File**: For each file you propose, provide a concise, one-sentence description of its purpose.
4.  **Format the Output**: Provide the design as a JSON object.

**Output Format:**
Respond with a JSON object that strictly adheres to the `ArchitecturePlan` schema.
{{
    "files": [
        {{
            "file_path": "path/to/new_file.py",
            "description": "A brief description of this file's purpose."
        }},
        {{
            "file_path": "path/to/another_file.py",
            "description": "Another brief description."
        }}
    ]
}}
If the existing file structure is sufficient, return an empty list: `{{"files": []}}`.
"""

class ArchitectureAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client)

    def run(
        self,
        goal: str,
        metadata: ProjectMetadata,
    ) -> ArchitecturePlan | None:
        print(f"[ArchitectureAgent] Designing architecture for: '{goal}'")

        prompt = PROMPT_TEMPLATE.format(
            goal=goal,
            file_list="\n".join(metadata.files),
        )

        response_model = self.llm_client.generate_json(prompt, output_schema=ArchitecturePlan)

        if not response_model or not response_model.files:
            print("[ArchitectureAgent] No architectural changes were proposed.")
            return None

        print(f"[ArchitectureAgent] Architecture design generated with {len(response_model.files)} files.")
        return response_model
