from typing import Dict, Any
from .base_stage import BaseStage

class ContextStage(BaseStage):
    """
    First stage of the pipeline.

    Currently, this stage is a placeholder. Its purpose is to prepare
    the initial context for the following stages. In the future, it could
    be used to enrich the initial configuration.
    """
    def __init__(self):
        # Calls the base class constructor with the name of this stage
        super().__init__(stage_name="Contextualization")

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"  -> {self.stage_name}: Analyzing request and deriving strategy.")
        config = state['request_config']

        derived_instructions: Dict[str, Any] = {}

        strategy_category = config.get('strategy', {}).get('category', '').lower()
        if 'news' in strategy_category or 'announcements' in strategy_category:
            derived_instructions['narrative_style'] = 'announcement'
        else:
            derived_instructions['narrative_style'] = 'standard'

        content_goal = config.get('generationConfig', {}).get('contentGoal', '').lower()
        derived_instructions['requires_cta'] = 'leads' in content_goal

        state['derived_instructions'] = derived_instructions
        print(f"     - Derived instructions: {derived_instructions}")

        return state