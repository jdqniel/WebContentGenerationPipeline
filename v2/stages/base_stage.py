# web_content_pipeline/stages/base_stage.py
from abc import ABC, abstractmethod

class PipelineStage(ABC):
    """Abstract base class for a pipeline stage."""
    @abstractmethod
    async def execute(self, context: dict) -> dict: # <-- Ahora es async def
        """
        Executes the logic of the stage asynchronously.
        """
        pass