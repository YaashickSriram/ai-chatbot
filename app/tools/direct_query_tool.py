from typing import Dict, Any, Optional

from app.tools.base_tool import BaseTool
from app.data.dataframe_manager import DataFrameManager


class DirectQueryTool(BaseTool):
    """
    Tool to retrieve a single value from the DataFrame
    using exact-match filters.
    """

    name = "direct_query_tool"
    description = "Fetches a single, precise value from the dataset using filters."

    def __init__(self, dataframe_manager: DataFrameManager):
        self.dataframe_manager = dataframe_manager

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expected params:
        {
            "column": "CLASSIFICATION_LEVEL",
            "filters": {
                "INITIATIVE_NAME": "Notse_T1_Plant6"
            }
        }
        """

        df = self.dataframe_manager.get_dataframe()

        column: Optional[str] = params.get("column")
        filters: Dict[str, Any] = params.get("filters", {})

        if not column or not filters:
            raise ValueError("'column' and 'filters' are required")

        # Apply filters
        for filter_column, value in filters.items():
            df = df[df[filter_column] == value]

        if df.empty:
            return {
                "column": column,
                "value": None,
                "message": "No matching record found"
            }

        value = df.iloc[0][column]

        return {
            "column": column,
            "value": value
        }
