from typing import Dict, Any
import pandas as pd
from app.tools.base_tool import BaseTool


class ComparisonTool(BaseTool):
    name = "comparison"
    description = "Compare counts between two groups"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expected params:
        {
            "df": pandas.DataFrame,
            "group_by": str,
            "values": list[str]   # exactly two values to compare
        }
        """
        df: pd.DataFrame = params["df"]
        group_by: str = params["group_by"]
        values: list[str] = params["values"]

        if group_by not in df.columns:
            raise ValueError(f"Invalid comparison column: {group_by}")

        if len(values) != 2:
            raise ValueError("Comparison requires exactly two values")

        result = {}

        for value in values:
            count = df[df[group_by] == value].shape[0]
            result[value] = count

        diff = result[values[1]] - result[values[0]]

        return {
            "tool": self.name,
            "comparison_type": "count",
            "group_by": group_by,
            "results": result,
            "difference": diff,
            "winner": values[1] if diff > 0 else values[0]
        }
