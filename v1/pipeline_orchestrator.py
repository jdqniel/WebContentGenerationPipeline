# WebContentGenerationPipeline/v1/pipeline_orchestrator.py
import os
from stages.stage_1_context import ContextStage
from stages.stage_2_generation import GenerationStage
from stages.stage_3_assembly import AssemblyStage
from utils.openai_client import OpenAIClient

PROMPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'prompts'))

class WebContentPipeline:
    def __init__(self):
        self.client = OpenAIClient()
        self.client.reset_costs() # Reiniciamos para una ejecución limpia

        self._stages = [
            ContextStage(),
            GenerationStage(
                client=self.client, # Le pasamos el cliente a la etapa
                content_prompt_path=os.path.join(PROMPTS_DIR, "v1_full_content_prompt.txt"),
                seo_prompt_path=os.path.join(PROMPTS_DIR, "v1_seo_assets_prompt.txt")
            ),
            AssemblyStage()
        ]
        print("V1 Two-Call Synchronous Pipeline initialized.")

    def run(self, config: dict) -> dict:
        pipeline_context = {"config": config}
        for stage in self._stages:
            print(f"Executing V1 Stage: {stage.__class__.__name__}")
            pipeline_context = stage.run(pipeline_context)
        
        cost_summary = self.client.get_cost_summary()
        return {"result": pipeline_context, "metrics": {"cost_summary": cost_summary}}