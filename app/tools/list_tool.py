from typing import Dict, Any, List

import pandas as pd

from app.tools.base_tool import BaseTool
from app.data.dataframe_manager import DataFrameManager


class ListTool(BaseTool):
    """
    Tool to list values or rows from the DataFrame based on filters.
    """

    name = "list_tool"
    description = "Lists values or records from the dataset based on filters."

    def __init__(self, dataframe_manager: DataFrameManager):
        self.dataframe_manager = dataframe_manager

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the list operation.

        Expected params:
        {
            "columns": ["COLUMN_1", "COLUMN_2"],   # optional
            "filters": {"REGION": "Africa"},       # optional
            "distinct": true,                      # optional
            "limit": 50                            # optional
        }
        """

        df = self.dataframe_manager.get_dataframe()

        columns: List[str] | None = params.get("columns")
        filters: Dict[str, Any] = params.get("filters", {})
        distinct: bool = params.get("distinct", False)
        limit: int | None = params.get("limit")

        # Step 1: Apply filters
        for column, value in filters.items():
            df = df[df[column] == value]

        # Step 2: Select columns
        if columns:
            df = df[columns]

        # Step 3: Remove duplicates if required
        if distinct:
            df = df.drop_duplicates()

        # Step 4: Apply limit
        if limit is not None:
            df = df.head(limit)

        return {
            "count": len(df),
            "items": df.to_dict(orient="records")
        }
