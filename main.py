# path: aida/main.py
# title: Main Application Entry Point
# role: Initializes the application, handles user input, and orchestrates the AI agents.

import sys
import signal
import shutil
from pathlib import Path
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file at the project root
project_root_for_env = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=project_root_for_env / ".env")


# プロジェクトルートをPythonパスに追加して、aidaパッケージを認識させる
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dependency_injector.wiring import inject, Provide
from aida.container import Container
from aida.orchestrator import Orchestrator
from aida.schemas import ProjectMetadata

# --- Path Definitions ---
# All paths are now correctly defined relative to the 'aida' directory itself.
AIDA_ROOT = Path(__file__).parent
WORKSPACE_DIR = AIDA_ROOT / "workspace"
CACHE_DIRS = [
    AIDA_ROOT / "aida_vectordb",
    AIDA_ROOT / "aida_sandbox",
]

# ◾️◾️◾️◾️◾️◾️◾️◾️◾️◾️◾️↓修正開始◾️◾️◾️◾️◾️◾️◾️◾️◾️◾️◾️
# sys.pathにworkspaceディレクトリを追加
sys.path.insert(0, str(WORKSPACE_DIR))
# ◾️◾️◾️◾️◾️◾️◾️◾️◾️◾️◾️↑修正終わり◾️◾️◾️◾️◾️◾️◾️◾️◾️◾️◾️


def setup_directories():
    """
    Ensures that the workspace directory exists and clears cache directories
    after user confirmation.
    """
    # Ensure the workspace directory exists.
    if not WORKSPACE_DIR.exists():
        print(f"[Main] Workspace directory not found. Creating at: {WORKSPACE_DIR}")
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    
    # --- Confirmation before cleaning up cache ---
    dirs_to_clean = [d for d in CACHE_DIRS if d.exists()]
    if dirs_to_clean:
        print("\n--- Cache Cleanup ---")
        print("The following cache/sandbox directories will be cleared:")
        for directory in dirs_to_clean:
            print(f"- {directory}")
        
        try:
            confirm = input("Do you want to proceed with cleanup? (y/n): ").lower()
            if confirm == 'y':
                print("--- Cleaning up cache directories ---")
                for directory in dirs_to_clean:
                    try:
                        shutil.rmtree(directory)
                        print(f"[Cleanup] Removed: {directory}")
                    except OSError as e:
                        print(f"Error removing directory {directory}: {e}")
                print("--- Cleanup Complete ---")
            else:
                print("--- Cleanup Skipped ---")
        except (KeyboardInterrupt, EOFError):
             print("\nCleanup cancelled. Exiting.")
             sys.exit(0)
    else:
        print("\n--- No cache directories to clean. ---")


def signal_handler(sig, frame):
    """
    Handles graceful shutdown on Ctrl+C by cleaning up cache directories.
    """
    print("\n[Main] Shutdown signal received. Cleaning up...")
    for directory in CACHE_DIRS:
         if directory.exists():
            try:
                shutil.rmtree(directory)
                print(f"[Cleanup] Removed: {directory}")
            except OSError as e:
                print(f"Error removing directory {directory}: {e}")
    sys.exit(0)

@inject
def main(orchestrator: Orchestrator = Provide[Container.orchestrator]):
    """
    The main application loop.
    """
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n--- AIDA: AI-Driven Assistant ---")
    print("Welcome! I'm here to help you with your software development tasks.")
    print("Type your request, or 'exit' to quit.")
    
    project_path = str(WORKSPACE_DIR)
    
    # Perform initial project setup and indexing once at the beginning.
    metadata = orchestrator.setup_project(project_path)
    
    try:
        while True:
            user_prompt = input("\nPrompt > ")
            if user_prompt.lower() == 'exit':
                print("Exiting AIDA. Goodbye!")
                break
            
            orchestrator.run_task(user_prompt, metadata, project_path)
            
            # After a task, re-analyze the workspace to get the latest state for the next prompt.
            print("\n--- Task finished. Updating project state for next command. ---")
            metadata = orchestrator.analysis_agent.run(project_root=project_path)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        # Perform initial setup and cleanup BEFORE initializing the container.
        # This ensures a clean state for the database and other components.
        setup_directories()
        
        container = Container()
        # main があるモジュールを明示的に指定
        container.wire(modules=[sys.modules[__name__]])
        main()
    except Exception as e:
        print(f"An error occurred during initialization: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # A final cleanup attempt on any exit path.
        print("\n--- Final Cleanup on Exit ---")
        for directory in CACHE_DIRS:
            if directory.exists():
                try:
                    shutil.rmtree(directory)
                    print(f"[Cleanup] Removed: {directory}")
                except OSError as e:
                    print(f"Error removing directory {directory}: {e}")