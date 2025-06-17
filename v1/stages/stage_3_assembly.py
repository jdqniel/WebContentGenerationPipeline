# WebContentGenerationPipeline/v1/stages/stage_3_assembly.py
from .base_stage import BaseStage

class AssemblyStage(BaseStage):
    """
    Etapa 3: Ensambla el diccionario final a partir de los datos
    pre-procesados por la GenerationStage.
    """
    def run(self, context: dict) -> dict:
        print("--- Executing Stage 3: Assembling Final Document ---")
        
        final_document = {
            "requestConfig": context.get("config", {}),
            "generatedContent": context.get("generated_content", {}),
            "seoAssets": context.get("seo_assets", {})
        }
        
        print("  - ✅ Final document assembled.")
        return final_document