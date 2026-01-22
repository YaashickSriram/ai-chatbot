from typing import Dict, Any
import pandas as pd

from app.tools.base_tool import BaseTool


class AggregationTool(BaseTool):
    name = "aggregation"

    def execute(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        operation = params.get("operation")
        group_by = params.get("group_by")
        column = params.get("column")

        # ----------------------------
        # Validate required params
        # ----------------------------
        if not operation:
            raise ValueError("Missing required parameter: operation")

        if not group_by:
            raise ValueError("Missing required parameter: group_by")

        # ----------------------------
        # Normalize columns FIRST
        # ----------------------------
        group_by = self._normalize_column(df, group_by)
        column = self._normalize_column(df, column) if column else None

        # ----------------------------
        # COUNT
        # ----------------------------
        if operation == "count":
            result = (
                df.groupby(group_by)
                .size()
                .reset_index(name="count")
                .to_dict(orient="records")
            )

        # ----------------------------
        # SUM / AVERAGE
        # ----------------------------
        elif operation in {"sum", "average"}:
            if not column:
                raise ValueError(f"'column' is required for operation '{operation}'")

            self._validate_numeric_column(df, column)

            agg_fn = "sum" if operation == "sum" else "mean"

            result = (
                df.groupby(group_by)[column]
                .agg(agg_fn)
                .reset_index(name=operation)
                .to_dict(orient="records")
            )

        else:
            raise ValueError(f"Unsupported operation: {operation}")

        return {
            "tool": self.name,
            "operation": operation,
            "group_by": group_by,
            "results": result,
        }
