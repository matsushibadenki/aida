# path: aida/agents/base_agent.py
# title: Base Agent
# role: Defines the abstract base class for all agents that use the LLM.

from abc import ABC, abstractmethod
from typing import Any

# Use a forward reference for the type hint to avoid circular imports
if 'LLMClient' not in globals():
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        # Corrected import path
        from aida.llm_client import LLMClient

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Ensures that each agent has an LLM client.
    """
    def __init__(self, llm_client: 'LLMClient'):
        """
        Initializes the agent with an LLM client.

        Args:
            llm_client (LLMClient): The client for interacting with the LLM.
        """
        self.llm_client = llm_client

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        The main execution method for the agent.
        This must be implemented by all subclasses.
        """
        pass