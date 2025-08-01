# path: aida/container.py
# title: Dependency Injection Container
# role: Defines and wires up the application's dependencies.

from dependency_injector import containers, providers
from pathlib import Path
from .llm_client import LLMClient
from .rag import VectorStore, RetrievalAgent, IndexingAgent
from .agents import (
    PlanningAgent,
    CodingAgent,
    AnalysisAgent,
    TestingAgent,
    DebuggingAgent,
    SearchAgent,
    ExecutionAgent, # Import the new agent
)
from .orchestrator import Orchestrator

class Container(containers.DeclarativeContainer):
    """
    The main dependency injection container for the AIDA application.
    It uses dependency-injector to manage and wire all components.
    """
    # --- Configuration ---
    config = providers.Configuration(
        yaml_files=[str(Path(__file__).parent / "config.yml")]
    )

    # --- LLM Client ---
    llm_client = providers.Singleton(
        LLMClient,
        llm_config=config.llm,
    )

    # --- RAG Components ---
    # Path is now correctly defined within the 'aida' directory.
    vector_store_path = providers.Object(str(Path(__file__).parent / "aida_vectordb"))
    vector_store = providers.Singleton(VectorStore, db_path=vector_store_path)
    
    retrieval_agent = providers.Factory(
        RetrievalAgent,
        vector_store=vector_store
    )
    
    indexing_agent = providers.Factory(
        IndexingAgent,
        vector_store=vector_store,
        chunk_size=config.rag.chunk_size,
        chunk_overlap=config.rag.chunk_overlap,
    )

    # --- Core Agents ---
    analysis_agent = providers.Factory(AnalysisAgent)
    testing_agent = providers.Factory(TestingAgent)
    search_agent = providers.Factory(SearchAgent) # Add SearchAgent
    execution_agent = providers.Factory(ExecutionAgent) # Add ExecutionAgent

    debugging_agent = providers.Factory(
        DebuggingAgent,
        llm_client=llm_client,
        retrieval_agent=retrieval_agent,
    )

    coding_agent = providers.Factory(
        CodingAgent,
        llm_client=llm_client,
        retrieval_agent=retrieval_agent,
    )

    planning_agent = providers.Factory(
        PlanningAgent,
        llm_client=llm_client
    )

    # --- Orchestrator ---
    orchestrator = providers.Singleton(
        Orchestrator,
        planning_agent=planning_agent,
        coding_agent=coding_agent,
        analysis_agent=analysis_agent,
        indexing_agent=indexing_agent,
        testing_agent=testing_agent,
        debugging_agent=debugging_agent,
        search_agent=search_agent, # Inject SearchAgent
        execution_agent=execution_agent, # Inject ExecutionAgent
        max_retries=config.max_retries
    )