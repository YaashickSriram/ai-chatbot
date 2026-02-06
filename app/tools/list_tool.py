import pandas as pd
from typing import Dict, Any
from app.tools.base_tool import BaseTool


class ListTool(BaseTool):
    """
    Tool for returning row-level records based on filters.
    """

    name = "list"
    description = "Returns records matching given conditions"

    _LOCATION_COLUMNS = [
        "SITE_NAME",
        "SITE_COUNTRY",
        "COUNTRY",
        "SITE_REGION",
        "ENTITY",
        "PLANT",
    ]

    def execute(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:

        filters = params.get("filters", {})
        contains = params.get("contains", {})

        # 🔧 NORMALIZATION FIX
        if isinstance(contains, str):
            contains = {
                "QUESTION_TEXT": contains
            }

        # 🔧 Semantic mappings (optional but safe)
        if "initiative" in params:
            filters["INITIATIVE_NAME"] = params["initiative"]

        if "year" in params:
            filters["EFFECTIVE_YEAR"] = params["year"]

        columns = params.get("columns")
        distinct = bool(params.get("distinct", False))
        limit = params.get("limit")

        def apply_location_search(dataframe: pd.DataFrame, value: Any) -> pd.DataFrame:
            location_columns = [
                col for col in self._LOCATION_COLUMNS if col in dataframe.columns
            ]
            if not location_columns:
                return dataframe

            text_value = str(value)
            mask = None
            for col in location_columns:
                col_mask = dataframe[col].astype(str).str.contains(
                    text_value, case=False, na=False
                )
                mask = col_mask if mask is None else mask | col_mask

            if mask is None:
                return dataframe
            return dataframe[mask]

        # Apply equality filters
        for column, value in filters.items():
            if column.lower() in {"location", "city", "country", "site", "region"}:
                df = apply_location_search(df, value)
                continue
            try:
                normalized_column = self._normalize_column(df, column)
            except ValueError:
                continue
            if normalized_column in self._LOCATION_COLUMNS and isinstance(value, str):
                df = apply_location_search(df, value)
                continue
            df = df[df[normalized_column] == value]

        # Apply text contains filters
        for column, text in contains.items():
            if column.lower() in {"location", "city", "country", "site", "region"}:
                df = apply_location_search(df, text)
                continue
            try:
                normalized_column = self._normalize_column(df, column)
            except ValueError:
                continue
            df = df[
                df[normalized_column]
                .astype(str)
                .str.contains(str(text), case=False, na=False)
            ]

        if columns:
            normalized_columns = []
            for column in columns:
                try:
                    normalized_columns.append(self._normalize_column(df, column))
                except ValueError:
                    continue
            if normalized_columns:
                df = df[normalized_columns]
                columns = normalized_columns

        if columns and (distinct or columns == ["INITIATIVE_NAME"]):
            df = df.drop_duplicates(subset=columns)

        if df.empty:
            return {
                "tool": self.name,
                "results": [],
                "value": None
            }

        if limit is not None:
            df = df.head(limit)

        return {
            "tool": self.name,
            "results": df.to_dict(orient="records"),
            "value": None
        }
