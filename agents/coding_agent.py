# path: aida/agents/coding_agent.py
# title: Coding Agent
# role: Generates and applies code changes based on a given task.

import os
from pathlib import Path
from typing import List
from .base_agent import BaseAgent
from ..schemas import CodeChange, ProjectMetadata, CodeChanges
from ..llm_client import LLMClient
from ..rag import RetrievalAgent

class CodingAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, retrieval_agent: RetrievalAgent):
        super().__init__(llm_client)
        self.retrieval_agent = retrieval_agent

    def run(self, task: str, metadata: ProjectMetadata) -> list[CodeChange]:
        print(f"[CodingAgent] Executing task: '{task}'")
        
        context = self.retrieval_agent.run(task)
        
        prompt = self._create_prompt(task, metadata, context)
        
        response_model = self.llm_client.generate_json(prompt, output_schema=CodeChanges)
        print("[CodingAgent] Code generated successfully.")
        return response_model.changes if response_model else []

    def apply_code_to_sandbox(self, code_changes: list[CodeChange], sandbox_path: str):
        """
        Applies the generated code changes to the sandbox environment.
        """
        workspace_root = Path(sandbox_path).resolve()

        for change in code_changes:
            target_path = (workspace_root / change.file_path).resolve()

            if not str(target_path).startswith(str(workspace_root)):
                print(f"Error: Security risk detected. Attempted to access a file outside the workspace: {change.file_path}")
                continue

            file_dir = target_path.parent
            file_dir.mkdir(parents=True, exist_ok=True)

            if change.action == "create" or change.action == "update":
                print(f"[CodingAgent] Writing to file: {target_path}")
                with open(target_path, "w", encoding='utf-8') as f:
                    f.write(change.content)
            elif change.action == "delete":
                if target_path.exists():
                    print(f"[CodingAgent] Deleting file: {target_path}")
                    target_path.unlink()

    def _create_prompt(self, task: str, metadata: ProjectMetadata, context: str) -> str:
        file_list_str = "\n".join(metadata.files) if metadata.files else "No files in the project."
        
        return f"""
        You are an expert programmer. Your task is to generate code changes based on the user's request.
        The user wants to: '{task}'.

        Analyze the project structure and relevant context to provide the necessary code modifications.
        The output should be a JSON object representing a list of code changes wrapped in a root object.

        Project Structure:
        {file_list_str}

        Relevant Code from similar files (Context):
        {context}
        
        Respond with a JSON object that strictly adheres to the `CodeChanges` schema.
        The root object should have a single key "changes" which contains a list of `CodeChange` objects.
        A `CodeChange` object has the following format:
        {{
            "file_path": "path/to/file.py",
            "action": "create" | "update" | "delete",
            "content": "the full content of the file for create/update, or empty for delete"
        }}
        
        IMPORTANT: The 'content' field must be a single-line JSON string. All newline characters within the code must be escaped as '\\n'.
        """