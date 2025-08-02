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
2.  **Review History & Current State:** What was the last action taken? What was its result?
3.  **Check for Completion:** Does the result of the last action fully satisfy the user's overall goal?
    - If the goal was to create a file and the file was just created, the task is done.
    - If the goal was to run a command and it executed successfully, the task is done.
    - If the answer to this is "Yes", then your next action MUST be `finish`.
4.  **Formulate a Simple, Direct Plan (if not complete):**
    - If the task is not yet complete, what is the next logical, atomic step?
    - **If the input is conversational, your action should be to chat.**
    - If the user asks to create a file and write code in it, combine this into a single step.
    - The plan should be a single, atomic action.
5.  **Determine the Immediate Next Action:** Based on your plan, what is the very next, single, atomic action to take? This action must be self-contained and generate complete, runnable code if it's a code action. **DO NOT USE PLACEHOLDERS.**

**Available Action Types:**
- `chat`: To respond to a conversational input. The description should be your response.
- `code`: To create a new file or modify existing code. The description must contain the FULL, complete code to be written to the specified file.
- `execute`: To run a command, like `python workspace/app.py`.
- `finish`: When the user's goal has been fully achieved. The description should be a summary of what was done.
- `clarify`: If you lack critical information to proceed.
- `error`: If an unrecoverable error occurred.

**Example Scenario 1: Task Completion**

* **Goal:** "Create a file named `app.py` and write a function that returns 'Hello, World!'."
* **History:**
    - AIDA Action: [code] Create a new file named `workspace/app.py` with the following complete content: ...
    - AIDA Result: Applied changes to 1 file(s).
* **Thought Process:**
    1.  **Goal:** Create `workspace/app.py` with a "Hello, World!" program.
    2.  **History:** The last action was to create this exact file, and the result was successful.
    3.  **Completion Check:** The last action achieved the user's goal.
    4.  **Next Action:**
        ```json
        {{
          "type": "finish",
          "description": "Successfully created `workspace/app.py` with the 'Hello, World!' program as requested."
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
