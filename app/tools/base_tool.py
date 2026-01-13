from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """
    Abstract base class for all Pandas tools.

    Tools are PURE computation units.
    They do NOT:
    - Call LLMs
    - Parse raw user text
    - Decide intent

    They ONLY:
    - Receive structured parameters
    - Execute pandas logic
    - Return structured results
    """

    name: str
    description: str

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool using structured parameters.

        Args:
            params (Dict[str, Any]):
                Parameters extracted by the ReAct agent
                (filters, group_by, operation, columns, etc.)

        Returns:
            Dict[str, Any]:
                JSON-serializable result used by the agent
                to generate the final user response.
        """
        raise NotImplementedError("Tool must implement execute()")
