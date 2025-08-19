# path: aida/agents/web_search_agent.py
# title: Web Search Agent
# role: Searches the web for information.

import os
from typing import Optional
# Corrected import from the new package
from langchain_google_community import GoogleSearchAPIWrapper

class WebSearchAgent:
    """
    An agent that uses the Google Search API to find information online.
    """
    def __init__(self, api_key: Optional[str] = None, cse_id: Optional[str] = None):
        """
        Initializes the WebSearchAgent.
        API keys can be provided directly or through environment variables.
        If keys are not available, the agent will be disabled.
        """
        self.search_wrapper = None
        # Prioritize provided arguments, then environment variables
        api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        cse_id = cse_id or os.environ.get("GOOGLE_CSE_ID")

        if api_key and cse_id:
            try:
                self.search_wrapper = GoogleSearchAPIWrapper(
                    google_api_key=api_key,
                    google_cse_id=cse_id
                )
                print("[WebSearchAgent] Initialized successfully.")
            except Exception as e:
                print(f"[WebSearchAgent] Error during initialization: {e}")
        else:
            print("[WebSearchAgent] Warning: API key or CSE ID not found. Web search will be disabled.")

    def run(self, query: str) -> str:
        """
        Runs a web search for the given query.

        Args:
            query: The search query.

        Returns:
            A string containing the search results, or an error message if disabled.
        """
        if not self.search_wrapper:
            return "Web search is disabled because the required API keys (GOOGLE_API_KEY, GOOGLE_CSE_ID) are not configured."

        print(f"[WebSearchAgent] Searching the web for: '{query}'")
        try:
            results = self.search_wrapper.run(query)
            return results
        except Exception as e:
            return f"An error occurred during web search: {e}"
