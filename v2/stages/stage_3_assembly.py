# web_content_pipeline/stages/stage_3_assembly.py
import uuid
from datetime import datetime, timezone
from .base_stage import PipelineStage

class AssemblyStage(PipelineStage):
    async def execute(self, context: dict) -> dict: # <-- Cambiado a async def
        print("--- Executing Stage 3: Final Assembly ---")
        usage_stats = context.get('usage_stats', {})
        generated_content = context.get('generated_content', {})
        seo_assets = context.get('seo_assets', {})

        final_output = {
            "generationId": str(uuid.uuid4()),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "usage_statistics": usage_stats,
            "requestConfig": context['config'],
            "generatedContent": generated_content,
            "seo_assets": seo_assets
        }
        print("Final output JSON assembled correctly.")
        return final_output