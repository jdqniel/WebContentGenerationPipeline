from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseStage(ABC):
    """
    Abstract base class for a stage in the processing pipeline.
    
    It defines the common interface that all concrete stages must implement.
    """
    def __init__(self, stage_name: str):
        """
        Initializes the stage with a descriptive name.
        """
        self.stage_name = stage_name

    @abstractmethod
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the main logic of the stage.
        
        This method must be implemented by all subclasses.
        
        Args:
            state: A dictionary containing the current state of the pipeline.
                   Each stage can read from and write to this state.
        
        Returns:
            The modified state dictionary.
        """
        pass