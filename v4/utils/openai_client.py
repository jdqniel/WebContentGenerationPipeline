import os
from openai import AsyncOpenAI
from typing import Optional

# Global variable to hold the client instance
_client: Optional[AsyncOpenAI] = None

def get_openai_async_client() -> AsyncOpenAI:
    """
    Returns a singleton instance of the AsyncOpenAI client.
    
    Initializes the client on the first call. The API key is automatically
    read from the OPENAI_API_KEY environment variable.
    """
    global _client
    if _client is None:
        print("Initializing AsyncOpenAI client...")
        # The API key is taken automatically from the environment
        _client = AsyncOpenAI()
    return _client