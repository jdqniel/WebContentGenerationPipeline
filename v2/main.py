import json
import random
import time
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Add project root to path to allow for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from v2.pipeline_orchestrator import WebContentPipeline

# Pricing for gpt-4o (per 1,000,000 tokens) in USD
GPT_4O_INPUT_COST_PER_MILLION_TOKENS = 5.00
GPT_4O_OUTPUT_COST_PER_MILLION_TOKENS = 15.00

def calculate_cost(usage_stats: dict) -> float:
    """Calculates the total cost based on token usage."""
    prompt_tokens = usage_stats.get("prompt_tokens", 0)
    completion_tokens = usage_stats.get("completion_tokens", 0)
    
    input_cost = (prompt_tokens / 1_000_000) * GPT_4O_INPUT_COST_PER_MILLION_TOKENS
    output_cost = (completion_tokens / 1_000_000) * GPT_4O_OUTPUT_COST_PER_MILLION_TOKENS
    
    return input_cost + output_cost

def load_mock_data(filepath: str):
    """Loads mock data from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file {filepath}.")
        return []

async def main():
    """
    Main function to run the v2 web content generation pipeline.
    """
    mock_data = load_mock_data("v2/data/mock_web_content_data.json")
    if not mock_data:
        print("Exiting due to data loading errors.")
        return

    sample_config = random.choice(mock_data)
    
    print("--- Running V2 Pipeline with Sample Config ---")
    print(json.dumps(sample_config, indent=2))
    print("------------------------------------------------")

    pipeline = WebContentPipeline()
    
    start_time = time.monotonic()
    final_result = await pipeline.run(sample_config)
    end_time = time.monotonic()
    
    execution_time = end_time - start_time
    
    output_path = "v2/output.json"

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Pipeline v2 finished successfully. Output saved to {output_path}")
    except IOError as e:
        print(f"🚨 Error writing output to file: {e}")

    # --- METRICS CALCULATION AND DISPLAY ---
    usage_stats = final_result.get("usage_statistics", {})
    total_cost = calculate_cost(usage_stats)

    print("\n--- V2 Pipeline Metrics ---")
    print(f"Execution Time: {execution_time:.2f} seconds")
    print("Cost Summary:")
    print(f"  - Prompt Tokens:     {usage_stats.get('prompt_tokens', 0)}")
    print(f"  - Completion Tokens: {usage_stats.get('completion_tokens', 0)}")
    print(f"  - Total Tokens:      {usage_stats.get('total_tokens', 0)}")
    print(f"  - Total Cost (USD):  ${total_cost:.6f}")
    print("---------------------------\n")

if __name__ == "__main__":
    asyncio.run(main())