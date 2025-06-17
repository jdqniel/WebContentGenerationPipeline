# WebContentGenerationPipeline/v1/utils/openai_client.py
import os
import json
from openai import OpenAI

# Precios para gpt-4o (por 1,000,000 de tokens) en USD
GPT_4O_INPUT_COST_PER_MILLION_TOKENS = 5.00
GPT_4O_OUTPUT_COST_PER_MILLION_TOKENS = 15.00

class OpenAIClient:
    def __init__(self):
        print("Initializing OpenAI client...")
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0

    def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = None):
        """Genera un objeto JSON y rastrea el uso de tokens."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                response_format={"type": "json_object"}, # Forzamos la salida JSON
                max_tokens=max_tokens
            )
            
            if response.usage:
                self._total_prompt_tokens += response.usage.prompt_tokens
                self._total_completion_tokens += response.usage.completion_tokens

            # La API con json_object garantiza un string JSON válido
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"🚨 An error occurred with the OpenAI API call: {e}")
            return None

    def get_cost_summary(self):
        """Calcula y devuelve el costo total."""
        input_cost = (self._total_prompt_tokens / 1_000_000) * GPT_4O_INPUT_COST_PER_MILLION_TOKENS
        output_cost = (self._total_completion_tokens / 1_000_000) * GPT_4O_OUTPUT_COST_PER_MILLION_TOKENS
        total_cost = input_cost + output_cost

        return {
            "total_prompt_tokens": self._total_prompt_tokens,
            "total_completion_tokens": self._total_completion_tokens,
            "total_cost_usd": total_cost,
        }

    def reset_costs(self):
        """Reinicia los contadores de tokens."""
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0