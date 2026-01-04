from typing import Dict, Any, Optional

import pandas as pd

from app.tools.base_tool import BaseTool
from app.data.dataframe_manager import DataFrameManager


class ComparisonTool(BaseTool):
    """
    Tool to compare aggregated values across different groups.
    """

    name = "comparison_tool"
    description = "Compares aggregated values across groups and identifies relative differences."

    def __init__(self, dataframe_manager: DataFrameManager):
        self.dataframe_manager = dataframe_manager

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute comparison.

        Expected params:
        {
            "column": "SCORE",                 # required
            "operation": "mean",               # required: count | sum | mean | min | max
            "group_by": "SITE_REGION",         # required
            "filters": {"YEAR": 2024}          # optional
        }
        """

        df = self.dataframe_manager.get_dataframe()

        column: Optional[str] = params.get("column")
        operation: Optional[str] = params.get("operation")
        group_by: Optional[str] = params.get("group_by")
        filters: Dict[str, Any] = params.get("filters", {})

        if not column or not operation or not group_by:
            raise ValueError(
                "'column', 'operation', and 'group_by' are required for comparison"
            )

        # Step 1: Apply filters
        for filter_column, value in filters.items():
            df = df[df[filter_column] == value]

        if df.empty:
            return {
                "message": "No data available for the given filters",
                "comparison": {}
            }

        # Step 2: Group and aggregate
        grouped_df = (
            df.groupby(group_by)[column]
            .agg(operation)
            .reset_index()
        )

        # Step 3: Convert to dictionary for comparison
        comparison: Dict[str, float] = {
            str(row[group_by]): float(row[column])
            for _, row in grouped_df.iterrows()
        }

        # Step 4: Determine highest and lowest values
        highest_group = max(comparison, key=lambda k: comparison[k]) 
        lowest_group = min(comparison, key=lambda k: comparison[k]) 

        return {
            "operation": operation,
            "column": column,
            "group_by": group_by,
            "comparison": comparison,
            "highest": {
                "group": highest_group,
                "value": comparison[highest_group]
            },
            "lowest": {
                "group": lowest_group,
                "value": comparison[lowest_group]
            }
        }
