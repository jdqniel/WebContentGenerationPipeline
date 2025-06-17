import os

from stages.stage_1_context import ContextStage
from stages.stage_2_generation import GenerationStage
from stages.stage_3_assembly import AssemblyStage

PROMPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'prompts'))

class WebContentPipeline:
    """Orchestrates the execution of stages to generate web content."""
    def __init__(self):
        self._stages = [
            ContextStage(), # Keeps its simple role
            GenerationStage(
                outline_prompt_path=os.path.join(PROMPTS_DIR,"1_outline_prompt.txt"),
                writer_prompt_path=os.path.join(PROMPTS_DIR,"2_section_writer_prompt.txt"),
                seo_prompt_path=os.path.join(PROMPTS_DIR, "3_seo_assets_prompt.txt")
            ),
            AssemblyStage()
        ]

    async def run(self, config: dict) -> dict: # <-- Cambiado a async def
        print(f"\n🚀 Starting pipeline for document type: '{config.get('documentType', 'N/A')}'")
        pipeline_context = {"config": config}
        for stage in self._stages:
            pipeline_context = await stage.execute(pipeline_context) # <-- Ahora es await
        print("✅ Pipeline finished successfully!")
        return pipeline_context