# WebContentGenerationPipeline/v1/stages/stage_1_context.py
import json
from .base_stage import BaseStage
import uuid
from datetime import datetime, timezone

class ContextStage(BaseStage):
    """
    Prepares the initial context and adds unique identifiers.
    """
    def run(self, config: dict) -> dict:
        print("  - Preparing context from initial config...")
        
        # Create a deep copy to avoid modifying the original config object
        context = json.loads(json.dumps(config))

        # Add unique identifiers for this run, like in V2
        context['generationId'] = str(uuid.uuid4())
        context['timestamp_utc'] = datetime.now(timezone.utc).isoformat()
        
        # The full context is ready for the next stage
        return context