from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


class BaseTool(ABC):
    """
    Base class for all tools.
    Provides shared validation and normalization utilities.
    """

    name: str = "base"

    @abstractmethod
    def execute(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    # -------------------------------------------------
    # Shared helpers
    # -------------------------------------------------

    def _normalize_column(
        self,
        df: pd.DataFrame,
        column: str
    ) -> Optional[str]:
        """
        Normalize user-provided column names to actual dataframe columns.

        - Case-insensitive
        - Trims whitespace
        - Converts spaces to underscores
        """

        if column is None:
            return None

        normalized = column.strip().replace(" ", "_").upper()

        for col in df.columns:
            if col.upper() == normalized:
                return col

        raise ValueError(f"Invalid column: {column}")

    def _validate_numeric_column(self, df: pd.DataFrame, column: str) -> None:
        """
        Ensure column exists and is numeric.
        """
        if column not in df.columns:
            raise ValueError(f"Invalid numeric column: {column}")

        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"Column '{column}' is not numeric")
