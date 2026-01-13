from typing import Dict, Any
import pandas as pd
from app.tools.base_tool import BaseTool


class DirectQueryTool(BaseTool):
    """
    Tool for single-value numeric queries.
    Examples:
    - total count
    - number of surveys
    """

    name = "direct"
    description = "Single numeric answers such as counts or totals"

    def execute(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a direct numeric query.

        Expected params:
        {
            "operation": "count",
            "filters": { "COLUMN": value }  # optional
        }
        """

        operation = params.get("operation", "count")
        filters = params.get("filters", {})

        # Apply filters if any
        for column, value in filters.items():
            if column not in df.columns:
                raise ValueError(f"Invalid column: {column}")
            df = df[df[column] == value]

        # Supported operations
        if operation == "count":
            result = len(df)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

        return {
            "tool": self.name,
            "operation": operation,
            "value": result
        }
