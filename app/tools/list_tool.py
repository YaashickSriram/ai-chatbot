import json
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
    params: Dict[str, Any]) -> Dict[str, Any]:
        
        filters = params.get("filters", {})
        contains = params.get("contains", {})
        # 🔧 NORMALIZATION FIX
        if isinstance(contains, str):
            contains = {
            "QUESTION_TEXT": contains
        }
            if isinstance(filters, dict):
        # Map semantic fields → real columns
             if "initiative" in params:
               filters["INITIATIVE_NAME"] = params["initiative"]
        if "year" in params:
            filters["YEAR"] = params["year"]

        columns = params.get("columns")
        limit = params.get("limit", 10)

    # Apply equality filters
        for column, value in filters.items():
          if column not in df.columns:
            continue
          df = df[df[column] == value]

    # Apply text contains filters
        for column, text in contains.items():
         if column not in df.columns:
            continue
         df = df[df[column].str.contains(text, case=False, na=False)]

        if columns:
         df = df[columns]

        return {
        "tool": "list",
        "results": df.head(limit).to_dict(orient="records")
         }
