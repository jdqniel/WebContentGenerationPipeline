from .base_stage import PipelineStage

class ContextStage(PipelineStage):
    # ... (el __init__ no cambia)
    async def execute(self, context: dict) -> dict: # <-- Cambiado a async def
        print("--- Executing Stage 1: Initializing Context ---")
        print("Context is ready for generation.")
        return context