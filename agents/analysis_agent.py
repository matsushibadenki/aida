# path: aida/agents/analysis_agent.py
# title: Analysis Agent
# role: Analyzes the project structure using ProjectAnalyzer.

from pathlib import Path
from aida.analysis import ProjectAnalyzer
from aida.schemas import ProjectMetadata

class AnalysisAgent:
    """
    Analyzes the project's file structure and returns structured metadata.
    This agent does not require an LLM client as it performs static analysis.
    """
    def __init__(self):
        """
        Initializes the AnalysisAgent.
        """
        print("AnalysisAgent initialized.")

    def run(self, project_root: str) -> ProjectMetadata:
        """
        Runs the analysis on the project using the dedicated analyzer.
        It lists all files and returns a ProjectMetadata object.

        Args:
            project_root: The absolute path to the project's root directory.

        Returns:
            A ProjectMetadata object containing the project's file structure.
        """
        if not Path(project_root).is_dir():
            raise ValueError(f"The provided path '{project_root}' is not a valid directory.")
            
        analyzer = ProjectAnalyzer(project_path=project_root)
        project_files = analyzer.list_files()
        
        metadata = ProjectMetadata(
            root_dir=str(analyzer.get_project_root()),
            files=project_files
        )
        
        print("Analysis complete. Metadata generated.")
        return metadata