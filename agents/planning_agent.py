# path: aida/agents/planning_agent.py
# title: Planning Agent
# role: Generates a step-by-step plan to achieve a user's goal.

from typing import List
from aida.llm_client import LLMClient
from aida.schemas import ProjectMetadata, Action, Plan
from aida.agents.base_agent import BaseAgent

PROMPT_TEMPLATE = """
You are an expert AI project planner. Your job is to create a step-by-step plan in JSON format.

**User's Goal:**
"{goal}"

**Existing Files:**
{file_list}

**Conversation History (for context):**
{history}

**Instructions:**
1.  Analyze the user's goal, files, and history.
2.  **For high-level goals like "build a web app", the FIRST step should be `design` to outline the file structure.** The description for the `design` action should be the user's high-level goal.
3.  **After a `design` action, your next step should be a `clarify` action to ask the user for approval before proceeding with coding.**
4.  If the user has already approved a design (visible in the history), create `code` steps to implement it.
5.  After any `code` action, add a `lint` action, followed by a `test` action.
6.  Use `refactor` when the user asks to improve existing code. The description should be the file path.
7.  Your output MUST be a JSON object with a "steps" key. The final step must always be `finish`.

**Example: High-Level Design Request**
* **Goal:** "Build a simple Flask API."
* **Existing Files:** (empty)
* **History:** (empty)
* **Correct JSON Output:**
```json
{{
  "steps": [
    {{
      "type": "design",
      "description": "Build a simple Flask API."
    }},
    {{
      "type": "clarify",
      "description": "I have designed the architecture for the Flask API. Should I proceed with generating the code for the proposed files?"
    }}
  ]
}}
```

**Example: Implementing an Approved Design**
* **Goal:** "The user approved the plan. Proceed with the implementation."
* **Existing Files:** (empty)
* **History:** "USER: Build a simple Flask API.
AIDA_ACTION: [design] Build a simple Flask API.
AIDA_DESIGN:
- app.py: The main Flask application file.
- test_app.py: Tests for the Flask application.
AIDA_ACTION: [clarify] I have designed the architecture...
USER_RESPONSE: yes"
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
      "description": "Create the main flask application file `workspace/app.py` as designed."
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
