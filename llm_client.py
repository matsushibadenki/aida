# path: aida/llm_client.py
# title: Large Language Model Client
# role: Interacts with the LLM provider to generate text and structured data.

import json
from typing import Type, TypeVar, Optional, Dict, Any
from langchain_ollama import ChatOllama
from pydantic import BaseModel, ValidationError
from .utils import clean_json_response

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    """
    A client for interacting with a large language model provider.
    This class supports generating structured JSON output.
    """
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initializes the LLMClient from a configuration dictionary.

        Args:
            llm_config: A dictionary containing LLM settings like provider, model, and host.
        """
        provider = llm_config.get("provider")
        model = llm_config.get("model")
        host = llm_config.get("host")

        if not all([provider, model, host]):
            raise ValueError("LLM config must include 'provider', 'model', and 'host'.")

        if provider.lower() != "ollama":
            raise NotImplementedError(f"Provider '{provider}' is not supported yet.")
        
        self.llm = ChatOllama(
            model=model,
            base_url=host,
        )
        print(f"LLMClient initialized with provider: {provider}, model: {model}, host: {host}")

    def generate_json(self, prompt: str, output_schema: Type[T]) -> Optional[T]:
        """
        Generates a structured JSON response by parsing the raw text output from the LLM.
        """
        try:
            raw_response = self.llm.invoke(prompt).content
            json_str = clean_json_response(raw_response)
            
            if not json_str:
                print("[LLMClient] Error: No valid JSON found in the LLM response.")
                print(f"--- Raw Response ---\n{raw_response}\n--------------------")
                return None
            
            parsed_json = json.loads(json_str)
            return output_schema.model_validate(parsed_json)

        except json.JSONDecodeError as e:
            print(f"[LLMClient] Error decoding JSON from LLM response: {e}")
            print(f"--- Cleaned JSON String ---\n{json_str}\n-------------------------")
            return None
        except ValidationError as e:
            print(f"[LLMClient] Error validating JSON against schema '{output_schema.__name__}': {e}")
            print(f"--- Parsed JSON ---\n{parsed_json}\n-------------------")
            return None
        except Exception as e:
            print(f"[LLMClient] An unexpected error occurred in generate_json: {e}")
            return None

    def generate_text(self, prompt: str) -> str:
        """
        Generates a plain text response from a prompt.
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else ""
        except Exception as e:
            print(f"[LLMClient] Error generating text: {e}")
            return ""