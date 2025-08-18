# path: aida/agents/planning_agent.py
# title: Planning Agent
# role: Generates a step-by-step plan to achieve a user's goal.

from typing import List
from aida.llm_client import LLMClient
from aida.schemas import ProjectMetadata, Action, Plan
from aida.agents.base_agent import BaseAgent

PROMPT_TEMPLATE = """
You are an expert AI project planner. Your job is to create a step-by-step plan in JSON format. The descriptions in your plan should be high-level instructions, NOT code.

**User's Goal:**
"{goal}"

**Existing Files:**
{file_list}

**Instructions:**
1.  Analyze the user's goal and existing files.
2.  Create a logical sequence of steps (`code`, `test`, `execute`).
3.  **IMPORTANT:** Descriptions for `code` actions should state WHAT to create (e.g., "Create a main file with an add function"), not the code itself.
4.  Do not include steps for files that already exist.
5.  The final step must be `finish`.
6.  Your output MUST be a JSON object with a "steps" key, containing a list of actions. Each action must have "type" and "description" keys.

**Example:**
* **Goal:** "Create `math_util.py` with an `add` function, create a test for it, and run the tests."
* **Existing Files:** (empty)
* **Correct JSON Output:**
```json
{{
  "steps": [
    {{
      "type": "code",
      "description": "Create the main file `workspace/math_util.py` with an `add` function."
    }},
    {{
      "type": "code",
      "description": "Create the test file `workspace/test_math_util.py` to test the `add` function."
    }},
    {{
      "type": "test",
      "description": "Run the test suite."
    }},
    {{
      "type": "finish",
      "description": "Task is complete."
    }}
  ]
}}
```

**Your Turn:**
Now, generate the plan for the user's goal. Respond with ONLY the `Plan` JSON object.
"""


class PlanningAgent(BaseAgent):
    """
    This agent is responsible for generating a step-by-step plan
    to achieve a user's goal.
    """

    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client)
        print("PlanningAgent initialized.")

    def run(self, goal: str, metadata: ProjectMetadata) -> Plan | None:
        """
        Generates a structured plan of actions to accomplish the goal.
        """
        print(f"[PlanningAgent] Generating a plan for goal: '{goal}'")

        file_list = metadata.files if hasattr(metadata, 'files') else []
        file_list_str = "\n".join(file_list) if file_list else "(empty)"

        # The last_result is not needed for planning, only the goal and current file state.
        prompt = PROMPT_TEMPLATE.format(
            goal=goal,
            file_list=file_list_str,
        )

        # Generate the description for the action
        plan = self.llm_client.generate_json(prompt, output_schema=Plan)
        if plan:
            print(f"[PlanningAgent] Plan generated with {len(plan.steps)} steps.")
        else:
            print("[PlanningAgent] Failed to generate a plan.")
        return plan
