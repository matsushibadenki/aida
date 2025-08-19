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

**Conversation History (for context):**
{history}

**Instructions:**
1.  Analyze the user's goal, existing files, and conversation history.
2.  **If the goal is ambiguous or lacks detail, your FIRST step MUST be a `clarify` action to ask the user for more information.**
3.  Create a logical sequence of steps. Available action types are `chat`, `code`, `lint`, `test`, `execute`, `web_search`, `git`, `dependency`, `clarify`.
4.  **After any `code` action that creates or modifies Python files, you should add a `lint` action to check the code quality.**
5.  **IMPORTANT:** Descriptions for `code` actions should state WHAT to create (e.g., "Create a main file with an add function"), not the code itself.
6.  Descriptions for `execute` actions MUST be a valid shell command.
7.  Descriptions for `git` actions MUST be a valid git command (e.g., "commit -am 'Refactor code'").
8.  Descriptions for `dependency` actions MUST be a valid pip command (e.g., "install requests").
9.  The final step must be `finish`.
10. Your output MUST be a JSON object with a "steps" key, containing a list of actions.

**Example: Code, Lint, and Test**
* **Goal:** "Create a simple flask app in `app.py` and a test for it."
* **Existing Files:** (empty)
* **Correct JSON Output:**
```json
{{
  "steps": [
    {{
      "type": "dependency",
      "description": "install flask pytest"
    }},
    {{
      "type": "code",
      "description": "Create the main flask application file `workspace/app.py`."
    }},
    {{
      "type": "lint",
      "description": "Run the linter on the new code."
    }},
    {{
      "type": "code",
      "description": "Create the test file `workspace/test_app.py` for the flask app."
    }},
    {{
      "type": "lint",
      "description": "Run the linter on the new test code."
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

    def run(self, goal: str, metadata: ProjectMetadata, history: List[str]) -> Plan | None:
        """
        Generates a structured plan of actions to accomplish the goal.
        """
        print(f"[PlanningAgent] Generating a plan for goal: '{goal}'")

        file_list = metadata.files if hasattr(metadata, 'files') else []
        file_list_str = "\n".join(file_list) if file_list else "(empty)"
        history_str = "\n".join(history) if history else "(no history)"

        prompt = PROMPT_TEMPLATE.format(
            goal=goal,
            file_list=file_list_str,
            history=history_str,
        )

        plan = self.llm_client.generate_json(prompt, output_schema=Plan)
        if plan:
            print(f"[PlanningAgent] Plan generated with {len(plan.steps)} steps.")
        else:
            print("[PlanningAgent] Failed to generate a plan.")
        return plan
