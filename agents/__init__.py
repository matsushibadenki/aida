# path: aida/agents/__init__.py
# title: AIDA Agents Package
# role: Exposes the agents used by the system.

from .analysis_agent import AnalysisAgent
from .coding_agent import CodingAgent
from .debugging_agent import DebuggingAgent
from .planning_agent import PlanningAgent
from .search_agent import SearchAgent
from .testing_agent import TestingAgent
from .execution_agent import ExecutionAgent
from .web_search_agent import WebSearchAgent
from .git_agent import GitAgent
from .dependency_agent import DependencyAgent
from .linting_agent import LintingAgent
from .refactoring_agent import RefactoringAgent
from .architecture_agent import ArchitectureAgent # Import new agent


__all__ = [
    "AnalysisAgent",
    "CodingAgent",
    "DebuggingAgent",
    "PlanningAgent",
    "SearchAgent",
    "TestingAgent",
    "ExecutionAgent",
    "WebSearchAgent",
    "GitAgent",
    "DependencyAgent",
    "LintingAgent",
    "RefactoringAgent",
    "ArchitectureAgent", # Export new agent
]
