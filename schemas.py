# path: aida/schemas.py
# title: Data Schemas
# role: Defines the Pantic models used for data exchange between agents.

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TaskState(Enum):
    """
    Represents the current state of the task execution workflow.
    This is now more flexible to represent the step in a dynamic plan.
    """
    PLANNING = "PLANNING"
    CHATTING = "CHATTING"
    SEARCHING = "SEARCHING"
    WEB_SEARCHING = "WEB_SEARCHING" # 追加
    CODING = "CODING"
    TESTING = "TESTING"
    EXECUTING = "EXECUTING"
    DEBUGGING = "DEBUGGING"
    FINISHING = "FINISHING"
    ERROR = "ERROR"


class Action(BaseModel):
    """
    Represents a single action to be taken by the orchestrator.
    The planning agent generates this.
    """
    type: str = Field(description="The type of action to take: 'chat', 'search', 'web_search', 'code', 'execute', 'test', 'finish', 'clarify', 'error'.") # 'web_search' を追加
    description: str = Field(description="A detailed description for the action, e.g., a search query, a coding instruction, or a command to run.")


class Plan(BaseModel):
    """
    Represents a sequence of actions to be executed to complete a task.
    """
    steps: List[Action] = Field(description="A list of actions to be executed in order.")


class CodeChange(BaseModel):
    """
    Represents a single file change, including the path and new content.
    """
    file_path: str = Field(description="The relative path to the file that needs to be changed.")
    action: str = Field(description="The action to perform: 'create', 'update', or 'delete'.")
    content: str = Field(description="The new content to be written to the file.")


class CodeChanges(BaseModel):
    """
    A wrapper for a list of CodeChange objects to be used as a structured output schema.
    """
    changes: List[CodeChange] = Field(description="A list of code changes to be applied.")


class ProjectMetadata(BaseModel):
    """
    Represents the metadata of the project being worked on.
    """
    root_dir: str = Field(description="The absolute path to the root directory of the project.")
    files: List[str] = Field(description="A list of all file paths within the project, relative to the root.")