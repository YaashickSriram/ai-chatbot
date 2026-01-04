from typing import Dict, Any, Optional

from click import Option
import pandas as pd

from app.tools.base_tool import BaseTool
from app.data.dataframe_manager import DataFrameManager


class AggregationTool(BaseTool):
    """
    Tool to perform aggregation operations on the DataFrame.
    """

    name = "aggregation_tool"
    description = "Performs aggregation operations like count, sum, mean, min, and max."

    def __init__(self, dataframe_manager: DataFrameManager):
        self.dataframe_manager = dataframe_manager

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute aggregation.

        Expected params:
        {
            "column": "SCORE",              # required
            "operation": "mean",            # required: count | sum | mean | min | max
            "group_by": "SITE_REGION",      # optional
            "filters": {"YEAR": 2024}       # optional
        }
        """

        df = self.dataframe_manager.get_dataframe()

        column: Optional[str] = params.get("column")
        operation: Optional[str] = params.get("operation")
        group_by: Optional[str] = params.get("group_by")
        filters: Dict[str, Any] = params.get("filters", {})

        if not column or not operation:
            raise ValueError("Both 'column' and 'operation' are required")

        # Step 1: Apply filters
        for filter_column, value in filters.items():
            df = df[df[filter_column] == value]

        # Step 2: Perform aggregation
        if group_by:
            result = (
                df.groupby(group_by)[column]
                .agg(operation)
                .reset_index()
            )

            return {
                "operation": operation,
                "column": column,
                "group_by": group_by,
                "result": result.to_dict(orient="records")
            }

        aggregated_value = getattr(df[column], operation)()

        return {
            "operation": operation,
            "column": column,
            "value": aggregated_value
        }
