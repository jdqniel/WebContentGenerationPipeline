import asyncio
import os
import sys
import json
import time
from dotenv import load_dotenv

# --- START: Configuration Block ---

# Add the project root to the path for module imports
# This is crucial for the script to be runnable directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from the .env file
load_dotenv()

# Import our other v3 modules
from v3.stages.stage_1_context import ContextStage
from v3.stages.stage_2_generation import GenerationStage
from v3.stages.stage_3_assembly import AssemblyStage
from v3.utils.openai_client import get_openai_async_client
from v3.config_generator import ConfigGenerator

# --- END: Configuration Block ---


class WebContentPipeline:
    """
    Orchestrates the execution of the different stages of the content pipeline.
    It defines the sequence and manages the data flow between stages.
    """

    def __init__(self):
        """Initializes the pipeline, loading the stages and prompt configuration."""
        # The path to the prompts is in this package's prompts folder
        prompts_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'prompts')
        )
        print(f"Looking for prompts at path: {prompts_path}")

        self.stages = [
            ContextStage(),
            GenerationStage(prompts_path=prompts_path),
            AssemblyStage()
        ]
        self.openai_client = get_openai_async_client()

    async def run(self, config: dict) -> dict:
        """
        Executes the pipeline sequentially, passing the state through each stage.
        """
        state = {"request_config": config}

        print("\n--- Starting Pipeline Execution ---")
        for stage in self.stages:
            print(f"Running Stage: {stage.stage_name}...")
            state = await stage.run(state)
        print("--- Finished Pipeline Execution ---\n")

        return state


# --- START: EXECUTION LOGIC ---

async def main():
    """
    Main function to run the V3 content generation pipeline.
    """
    print("🚀 Starting V3 Content Generation Pipeline...")
    start_time = time.monotonic()

    # 1. Initialize the configuration generator
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    config_generator = ConfigGenerator(data_path=data_path)

    # 2. Generate a random configuration for this run
    print("\n--- Generating New Random Configuration ---")
    request_config = config_generator.generate_random_config()
    print(json.dumps(request_config, indent=2))
    print("-----------------------------------------\n")

    # 3. Initialize and run the pipeline
    pipeline = WebContentPipeline()
    final_result = await pipeline.run(request_config)

    # 4. Calculate metrics and save the result
    execution_time = time.monotonic() - start_time
    job_details = final_result.get('job_details', {})
    generation_id = job_details.get('generation_id', 'unknown')
    base_dir = os.path.dirname(__file__)
    output_root = os.path.join(base_dir, 'output')
    job_dir = os.path.join(output_root, generation_id)
    os.makedirs(job_dir, exist_ok=True)
    output_filename = os.path.join(job_dir, f"v3_output_{generation_id}.json")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=4, ensure_ascii=False)

    print(f"\n--- ✅ V3 Pipeline Complete ---")
    print(f"⏱️  Total Execution Time: {execution_time:.2f} seconds")
    print(f"🆔 Generation ID: {generation_id}")
    print(f"📂 Output directory: {job_dir}")
    print(f"📄 Result saved to: {output_filename}")

    txt_filename = os.path.join(job_dir, f"v3_output_{generation_id}.txt")
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(final_result["content_details"]["full_content"])
    print(f"📝 Raw content saved to: {txt_filename}")
    print("----------------------------\n")

if __name__ == "__main__":
    # Ensure the API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("🚨 Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file in the project root and add your API key.")
    else:
        # Run the async main function
        asyncio.run(main())

# --- END: EXECUTION LOGIC ---