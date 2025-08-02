# path: aida/agents/planning_agent.py
# title: Planning Agent
# role: Generates a description for a specific action based on the current task state.

from typing import List
from ..llm_client import LLMClient
from ..schemas import ProjectMetadata, Action, TaskState
from .base_agent import BaseAgent

PROMPT_TEMPLATE = """
You are an expert AI Project Manager. Your task is to look at a user's goal and the current project state, and decide the single next action to take.

**User's Overall Goal:**
"{goal}"

**Project File Structure:**
{file_list}

**Conversation History (including previous results):**
{history_with_results}

**Your Task:**
Based on all the information above, decide on the single most effective next action.

**Your Thought Process (Chain of Thought) - FOLLOW THIS STRICTLY:**
1.  **Analyze Goal:** What does the user want to do? (e.g., "Create and run a file to calculate Pi.")
2.  **Check File Existence:** Does the file needed for the goal (e.g., `workspace/test.py`) exist in the "Project File Structure" above?
3.  **Decide Next Action:**
    * **If the file does NOT exist:** The next action MUST be `code` to create the file. Do not try to execute, test, or finish.
    * **If the file DOES exist and was just created:** The next logical step is probably to `execute` it to see if it works.
    * **If the file was just executed successfully:** The goal is likely complete. The next action should be `finish`.
    * **If the user is just chatting:** The action should be `chat`.
4.  **Verify Action:** Ensure your chosen action is logical based on the history and file list. For a `code` action, ensure you are implementing the user's *full* request (e.g., for "独自の円周率," implement an actual algorithm like Leibniz, don't use `math.pi`).

**Available Action Types:**
- `code`: To create or modify a file. The `description` **MUST** start with "Create a new file named `path/to/file.ext`..." or "Update the file named `path/to/file.ext`...", followed by the complete code.
- `execute`: To run a command, like `python workspace/test.py`.
- `finish`: When the user's goal has been fully achieved.
- `chat`: To respond to a conversational input.
- `clarify`: If you need more information.
- `error`: If something is unrecoverable.

**Example Scenario: Create and Run**

* **Goal:** "python形式で、test.pyに独自の円周率を求めるコードを書いて表示出来るようにしてください"
* **File Structure (Turn 1):** `(empty)`
* **History (Turn 1):** `(empty)`
* **Thought Process (Turn 1):**
    1. **Goal:** Create `workspace/test.py` with a Pi algorithm and run it.
    2. **File Check:** `workspace/test.py` does not exist.
    3. **Next Action:** Must be `code`.
    4. **Verify:** The `code` action should implement a real algorithm.
        ```json
        {{
          "type": "code",
          "description": "Create a new file named `workspace/test.py` with the following complete content:\\n```python\\ndef calculate_pi_leibniz(iterations: int) -> float:\\n    pi_sum = 0.0\\n    for i in range(iterations):\\n        term = ((-1) ** i) / (2 * i + 1)\\n        pi_sum += term\\n    return pi_sum * 4\\n\\nif __name__ == \\"__main__\\":\\n    pi_approximation = calculate_pi_leibniz(100000)\\n    print(f\\"Pi approximation (Leibniz): {{pi_approximation}}\\" )\\n```"
        }}
        ```
* **File Structure (Turn 2):** `workspace/test.py`
* **History (Turn 2):** "Last Action Result: Applied changes to 1 file(s)."
* **Thought Process (Turn 2):**
    1. **Goal:** Create and run the Pi script.
    2. **File Check:** `workspace/test.py` now exists.
    3. **Next Action:** The file was just created, so the next step is `execute`.
        ```json
        {{
          "type": "execute",
          "description": "python workspace/test.py"
        }}
        ```

**Your Turn:**
Now, analyze the current request: "{goal}"
Provide the next action based on the strict thought process above.

**Final Output:**
Provide **ONLY** the final JSON object for the next action. Do not include your thought process in the final output. The JSON must be raw and strictly adhere to the `Action` schema.
"""


class PlanningAgent(BaseAgent):
    """
    This agent is responsible for generating a description for a specific action
    based on the current state of the task execution workflow.
    """

    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client)
        print("PlanningAgent initialized.")

    def run(self, goal: str, metadata: ProjectMetadata, history: str, last_result: str) -> Action | None:
        """
        Determines the description for the next action based on the current state.
        """
        print(f"[PlanningAgent] Deciding next action...")

        file_list = metadata.files if hasattr(metadata, 'files') else []
        # Make file paths relative to the workspace for the prompt
        workspace_path_str = "workspace/"
        display_files = [f.split(workspace_path_str, 1)[-1] for f in file_list if workspace_path_str in f]
        file_list_str = "\n".join(display_files) if display_files else "(empty)"


        # Combine history and last result for a more complete context
        history_with_results = f"{history}\nLast Action Result: {last_result}"

        prompt = PROMPT_TEMPLATE.format(
            goal=goal,
            file_list=file_list_str,
            history_with_results=history_with_results,
        )

        # Generate the description for the action
        action_plan = self.llm_client.generate_json(prompt, output_schema=Action)

        return action_plan
