# path: aida/orchestrator.py
# title: Task Orchestrator
# role: Manages the stateful workflow of AI agents to accomplish development tasks.

import typing
from pathlib import Path
import shutil
from .schemas import ProjectMetadata, Action, TaskState, CodeChange
from .utils import sandbox_manager

if typing.TYPE_CHECKING:
    from .agents import (
        PlanningAgent,
        CodingAgent,
        AnalysisAgent,
        TestingAgent,
        DebuggingAgent,
        SearchAgent,
        ExecutionAgent,
    )
    from .rag import IndexingAgent


class Orchestrator:
    """
    The Orchestrator coordinates the different agents to execute a user's request
    through a stateful, flexible workflow.
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
        Executes a user-defined task through a flexible, action-driven workflow.
        """
        print(f"\n--- Running Task: {prompt} ---")

        conversation_history = [f"User: {prompt}"]
        last_result = "Task started."
        last_code_changes: list[CodeChange] = []
        task_successful = False

        with sandbox_manager(project_path) as sandbox_path:
            current_metadata = metadata
            
            for i in range(self.max_retries * 3): # Increased loop limit for more complex tasks
                
                action = self.planning_agent.run(
                    goal=prompt,
                    metadata=current_metadata,
                    history="\n".join(conversation_history),
                    last_result=last_result,
                )

                if not action:
                    print("\n--- ⚠️ Task Stopped: Planning agent did not return an action. ---")
                    break

                print(f"\n>>> Step {i+1}: [{action.type}] {action.description} <<<")
                conversation_history.append(f"AIDA Action: [{action.type}] {action.description}")

                if action.type == "finish":
                    task_successful = True
                    print("\n--- ✅ Task Completed Successfully ---")
                    break
                
                if action.type == "error":
                    print(f"--- ❌ Task Failed: {action.description} ---")
                    break

                # --- Action Execution ---
                if action.type == "search":
                    search_results = self.search_agent.run(sandbox_path, action.description)
                    last_result = f"Found {len(search_results)} matching files:\n" + "\n".join(search_results)
                    print(last_result)

                elif action.type == "code":
                    code_changes = self.coding_agent.run(action.description, current_metadata)
                    if not code_changes:
                        last_result = "Coding agent did not produce any code. Please check the plan."
                        print(f"[Orchestrator] {last_result}")
                    else:
                        self.coding_agent.apply_code_to_sandbox(code_changes, sandbox_path)
                        last_code_changes = code_changes
                        last_result = f"Applied changes to {len(code_changes)} file(s)."
                        print(f"[Orchestrator] {last_result}")
                        # Re-analyze the project after code changes
                        current_metadata = self.analysis_agent.run(project_root=sandbox_path)
                
                elif action.type == "execute":
                    success, output = self.execution_agent.run(sandbox_path, action.description)
                    last_result = f"Execution finished. Success: {success}\nOutput:\n{output}"
                    print(output)

                elif action.type == "test":
                    tests_passed, test_output = self.testing_agent.run_tests(sandbox_path)
                    print(test_output) # Show test results immediately
                    
                    if tests_passed:
                        last_result = "All tests passed."
                        print(f"--- ✅ {last_result} ---")
                    else:
                        last_result = f"Tests failed.\n{test_output}"
                        print("--- ❌ Tests Failed. Attempting to debug... ---")
                        # Enter debugging loop
                        fixed_code = self.debugging_agent.run(
                            goal=prompt,
                            sandbox_path=sandbox_path,
                            test_output=test_output,
                            metadata=current_metadata
                        )
                        if fixed_code:
                            self.coding_agent.apply_code_to_sandbox(fixed_code, sandbox_path)
                            last_code_changes = fixed_code
                            last_result = "Applied a potential fix from the debugging agent. Re-running tests in the next step."
                            print("[Orchestrator] " + last_result)
                            # Re-analyze after applying the fix
                            current_metadata = self.analysis_agent.run(project_root=sandbox_path)
                        else:
                            last_result = "Debugging agent could not generate a fix. The task has failed."
                            print(f"--- ❌ {last_result} ---")
                            break # Exit the main loop if debugging fails
                
                elif action.type == "clarify":
                    # In a real application, this would pause and prompt the user.
                    # Here, we will just print the clarification question and consider the task "done" for now.
                    print(f"\n--- 🤔 Clarification Needed ---")
                    last_result = "Awaiting user clarification."
                    task_successful = True # It's not a failure, just a pause.
                    break

                else:
                    last_result = f"Unknown action type: {action.type}. Please choose from the available types."
                    print(f"--- ⚠️ {last_result} ---")
                
                conversation_history.append(f"AIDA Result: {last_result}")


            if not task_successful:
                print(f"\n--- ❌ Task Failed: Reached maximum loop iterations or an unhandled error occurred. ---")
            
            # --- Sync changes back to the main workspace if successful ---
            if task_successful and last_code_changes:
                print(f"\n[Orchestrator] Syncing changes from sandbox to workspace '{project_path}'...")
                # We need to copy the contents of the sandbox, not the sandbox dir itself
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

            # Final analysis of the workspace for the next prompt
            print("\n--- Task finished. Updating project state for next command. ---")
            metadata = self.analysis_agent.run(project_root=project_path)