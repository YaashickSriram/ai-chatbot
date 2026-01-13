from typing import Dict, Any, List
import pandas as pd
from app.tools.base_tool import BaseTool


class ListTool(BaseTool):
    """
    Tool for returning row-level records based on filters.
    """

    name = "list"
    description = "Returns records matching given conditions"

    def execute(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a list query.

        Expected params:
        {
            "filters": { "COLUMN": value },           # optional
            "contains": { "COLUMN": "text" },         # optional (case-insensitive)
            "columns": ["COL1", "COL2"],               # optional
            "limit": 10                                # optional
        }
        """

        filters: Dict[str, Any] = params.get("filters", {})
        contains: Dict[str, str] = params.get("contains", {})
        columns: List[str] | None = params.get("columns")
        limit: int | None = params.get("limit")

        # Apply equality filters
        for column, value in filters.items():
            if column not in df.columns:
                raise ValueError(f"Invalid filter column: {column}")
            df = df[df[column] == value]

        # Apply text contains filters (case-insensitive)
        for column, text in contains.items():
            if column not in df.columns:
                raise ValueError(f"Invalid contains column: {column}")
            df = df[df[column].astype(str).str.contains(text, case=False, na=False)]

        # Select columns if specified
        if columns:
            missing = set(columns) - set(df.columns)
            if missing:
                raise ValueError(f"Missing columns: {missing}")
            df = df[columns]

        # Apply limit
        if limit is not None:
            df = df.head(limit)

        return {
            "tool": self.name,
            "row_count": len(df),
            "records": df.to_dict(orient="records")
        }
