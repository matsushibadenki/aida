# path: aida/agents/planning_agent.py
# title: Planning Agent
# role: Generates a description for a specific action based on the current task state.

from typing import List
from ..llm_client import LLMClient
from ..schemas import ProjectMetadata, Action, TaskState
from .base_agent import BaseAgent

PROMPT_TEMPLATE = """
You are an expert AI Project Manager and Lead Developer. Your primary goal is to understand a user's request and create a simple, direct plan to achieve it. You must be meticulous, avoid making assumptions, and stick to the user's request.

**User's Overall Goal:**
"{goal}"

**Project File Structure:**
{file_list}

**Conversation History (including previous results):**
{history_with_results}

**Your Task:**
Based on all the information above, decide on the single most effective next action.

**Your Thought Process (Chain of Thought) - FOLLOW THIS STRICTLY:**
1.  **Analyze the Goal:** What is the user's explicit request?
    - For example: "Create a file `test.py` and write a program to calculate pi."
2.  **Assess the Current State:**
    - Does the requested file (`workspace/test.py`) already exist?
    - What was the result of the last action?
3.  **Formulate a Simple, Direct Plan:**
    - **Adhere strictly to the user's request.** Do not add extra features, files, or test frameworks unless explicitly asked.
    - If the user asks to create a file and write code in it, combine this into a single step.
    - The plan should be a single, atomic action that accomplishes the goal.
4.  **Determine the Immediate Next Action:** Based on your simple plan, what is the very next, single, atomic action to take? This action must be self-contained and generate complete, runnable code. **DO NOT USE PLACEHOLDERS.**

**Available Action Types:**
- `code`: To create a new file or modify existing code. The description must contain the FULL, complete code to be written to the specified file.
- `execute`: To run a command, like `python workspace/app.py`.
- `finish`: When the user's goal has been fully achieved.
- `clarify`: If you lack critical information to proceed.
- `error`: If an unrecoverable error occurred.

**Example Scenario:**

* **Goal:** "Create a file named `app.py` and write a function that returns 'Hello, World!'."
* **Thought Process:**
    1.  **Goal:** Create `workspace/app.py` and write a "Hello, World!" program in it.
    2.  **State:** The file `workspace/app.py` does not exist.
    3.  **Plan:** Create the file `workspace/app.py` with all the necessary code in one go.
    4.  **Next Action:**
        ```json
        {{
          "type": "code",
          "description": "Create a new file named `workspace/app.py` with the following complete content:\\n```python\\ndef say_hello():\\n    return \\"Hello, World!\\"\\n\\nif __name__ == \\"__main__\\":\\n    print(say_hello())\\n```"
        }}
        ```

**Your Turn:**
Now, analyze the current request: "{goal}"
The file list is: {file_list}
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
        file_list_str = "\n".join([f for f in file_list if not f.endswith('.DS_Store')]) # Filter out .DS_Store

        # Combine history and last result for a more complete context
        history_with_results = f"{history}\nLast Action Result: {last_result}"

        prompt = PROMPT_TEMPLATE.format(
            goal=goal,
            file_list=file_list_str if file_list_str else "No files in the project yet.",
            history_with_results=history_with_results,
        )

        # Generate the description for the action
        action_plan = self.llm_client.generate_json(prompt, output_schema=Action)

        return action_plan