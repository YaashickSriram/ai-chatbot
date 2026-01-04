from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """
    Abstract base class for all Pandas tools.

    Every tool must:
    - Have a name
    - Have a description
    - Implement execute()
    """

    name: str
    description: str

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with structured parameters.

        Args:
            params (dict): Parameters extracted by the agent.

        Returns:
            dict: Structured result (JSON-serializable).
        """
        pass
