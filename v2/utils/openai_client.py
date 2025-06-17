# web_content_pipeline/utils/openai_client.py
from openai import AsyncOpenAI # <-- Importamos la versión Async
import os

print("Initializing Async OpenAI client...")
try:
    # Instanciamos el cliente asíncrono
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️ Warning: OPENAI_API_KEY environment variable is not set. API calls will fail.")
except TypeError:
    print("🚨 Error: OPENAI_API_KEY environment variable is not set.")
    client = None