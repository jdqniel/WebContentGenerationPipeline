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
        """
        Executes the contextualization stage.

        For now, it simply prints a message and passes the state to the
        next stage without modification.
        """
        print(f"  -> {self.stage_name}: Preparing context for generation.")
        
        # No modifications are made to the state in this version.
        return state