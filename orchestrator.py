# path: aida/orchestrator.py
# title: Task Orchestrator
# role: Manages the stateful workflow of AI agents to accomplish development tasks.

import typing
from pathlib import Path
import shutil
from aida.schemas import ProjectMetadata, Action, TaskState, CodeChange
from aida.utils import sandbox_manager

if typing.TYPE_CHECKING:
    from aida.agents import (
        PlanningAgent,
        CodingAgent,
        AnalysisAgent,
        TestingAgent,
        DebuggingAgent,
        SearchAgent,
        ExecutionAgent,
    )
    from aida.rag import IndexingAgent


class Orchestrator:
    """
    The Orchestrator coordinates the different agents to execute a user's request
    by first generating a plan and then executing it step-by-step.
    """
    def __init__(
        self,
        planning_agent: "PlanningAgent",
        coding_agent: "CodingAgent",
        analysis_agent: "AnalysisAgent",
        indexing_agent: "IndexingAgent",
        testing_agent: "TestingAgent",
        debugging_agent: "DebuggingAgent",
        search_agent: "SearchAgent",
        execution_agent: "ExecutionAgent",
        max_retries: int,
    ):
        self.planning_agent = planning_agent
        self.coding_agent = coding_agent
        self.analysis_agent = analysis_agent
        self.indexing_agent = indexing_agent
        self.testing_agent = testing_agent
        self.debugging_agent = debugging_agent
        self.search_agent = search_agent
        self.execution_agent = execution_agent
        self.max_retries = max_retries
        print("Orchestrator initialized with all agents.")

    def setup_project(self, project_path: str) -> ProjectMetadata:
        """
        Analyzes the project directory and performs a full indexing of its content.
        """
        print("\n--- Setting up Project Environment ---")
        print(f"Running analysis on project: {project_path}")
        metadata = self.analysis_agent.run(project_root=project_path)
        print("Analysis complete. Metadata generated.")

        self.indexing_agent.run_full_index(project_path, metadata.files)
        print("--- Project Setup Complete ---")
        return metadata

    def run_task(self, prompt: str, metadata: ProjectMetadata, project_path: str):
        """
        Generates a plan and executes it step-by-step.
        """
        print(f"\n--- Running Task: {prompt} ---")

        # 1. Generate the plan
        plan = self.planning_agent.run(prompt, metadata)
        if not plan or not plan.steps:
            print("\n--- ❌ Task Failed: Could not generate a valid plan. ---")
            return

        last_code_changes: list[CodeChange] = []
        task_successful = False

        with sandbox_manager(project_path) as sandbox_path:
            current_metadata = metadata
            
            # 2. Execute the plan step-by-step
            for i, action in enumerate(plan.steps):
                print(f"\n>>> Step {i+1}/{len(plan.steps)}: [{action.type}] {action.description} <<<")

                if action.type == "finish":
                    task_successful = True
                    print("\n--- ✅ Task Completed Successfully ---")
                    break
                
                if action.type == "error":
                    print(f"--- ❌ Task Failed: {action.description} ---")
                    break

                # --- Action Execution ---
                if action.type == "code":
                    code_changes = self.coding_agent.run(action.description, current_metadata)
                    if not code_changes:
                        print(f"[Orchestrator] Coding agent did not produce any code. Skipping step.")
                    else:
                        self.coding_agent.apply_code_to_sandbox(code_changes, sandbox_path)
                        last_code_changes = code_changes
                        print(f"[Orchestrator] Applied changes to {len(code_changes)} file(s).")
                        # Re-analyze the project after code changes to keep metadata fresh
                        current_metadata = self.analysis_agent.run(project_root=sandbox_path)
                
                elif action.type == "execute":
                    success, output = self.execution_agent.run(sandbox_path, action.description)
                    print(output)
                    if not success:
                        print(f"--- ❌ Execution Failed. Stopping task. ---")
                        break

                elif action.type == "test":
                    tests_passed, test_output = self.testing_agent.run_tests(sandbox_path)
                    print(test_output)
                    
                    if not tests_passed:
                        print("--- ❌ Tests Failed. Stopping task. Debugging is not yet implemented in this loop. ---")
                        # Here you could insert the debugging loop if needed
                        break
                
                else:
                    print(f"--- ⚠️ Unknown action type: {action.type}. Skipping. ---")

            if not task_successful:
                print(f"\n--- ❌ Task Failed: Plan did not complete successfully. ---")
            
            # --- Sync changes back to the main workspace if successful ---
            if task_successful and last_code_changes:
                print(f"\n[Orchestrator] Syncing changes from sandbox to workspace '{project_path}'...")
                for item in Path(sandbox_path).iterdir():
                    source_path = item
                    destination_path = Path(project_path) / item.name
                    if source_path.is_dir():
                        if destination_path.exists():
                             shutil.rmtree(destination_path)
                        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_path, destination_path)

                print("[Orchestrator] Sync complete.")
                self.indexing_agent.update_index(project_path, last_code_changes)
