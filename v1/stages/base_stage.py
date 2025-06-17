# WebContentGenerationPipeline/v1/stages/base_stage.py
from abc import ABC, abstractmethod

class BaseStage(ABC):
    @abstractmethod
    def run(self, context: dict) -> dict:
        """
        Executes the logic for this stage of the pipeline.

        Args:
            context (dict): The data passed from the previous stage.

        Returns:
            dict: The data to be passed to the next stage.
        """
        pass