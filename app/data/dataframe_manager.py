# import os
# import pandas as pd
# from typing import Any, Optional, Callable
# from datetime import datetime, timedelta
# import logging

# from app.data.snowflake_connector import SnowflakeConnector
# from app.config import settings

# class DataFrameManager:
#     """
#     Manages loading, caching, refreshing, and safe access
#     to an in-memory Pandas DataFrame sourced from Snowflake.
#     """

#     def __init__(self, snowflake_connector: SnowflakeConnector):
#         self.connector = snowflake_connector
#         self.df: Optional[pd.DataFrame] = None
#         self.last_refresh: Optional[datetime] = None

#     def load_data(self, table_name: Any = settings.SF_TABLE):
#         """
#         Load data from Snowflake into the DataFrame.
#         """

#         query = f"SELECT * FROM {table_name}"

#         self.df = self.connector.fetch_data(query)
#         self.last_refresh = datetime.now() # will refresh the data every time fetch_data() is called so needed timestamp of last refresh

#         self._preprocess_data()

#     def _preprocess_data(self):
#         """
#         Preprocess DataFrame (handle dates, nulls, types).
#         """
#         if self.df is None:
#             return "Dataframe has NONE"

#         # Convert date-like columns to datetime
#         object_columns = self.df.select_dtypes(include=["object"]).columns
#         for col in object_columns:
#             if "date" in col.lower(): #use regex
#                 self.df[col] = pd.to_datetime(self.df[col], errors="coerce")

#         # Placeholder for future preprocessing
#         # (null handling, normalization, etc.)

#     def refresh_if_needed(self):
#         """
#         Refresh data if cache is older than configured threshold.
#         """
#         if (
#             self.last_refresh is None or
#             datetime.now() - self.last_refresh >
#             timedelta(seconds=settings.DATA_REFRESH_INTERVAL)
#         ):
#             self.load_data()

#     def get_dataframe(self) -> pd.DataFrame:
#         """
#         Return a safe copy of the cached DataFrame.
#         """
#         self.refresh_if_needed()

#         if self.df is None:
#             raise RuntimeError("DataFrame not loaded")

#         return self.df.copy()

#     def execute_query(self, query_func: Callable[[pd.DataFrame], pd.DataFrame]) -> pd.DataFrame:
#         """
#         Execute a Pandas query function safely on the DataFrame.
#         """
#         self.refresh_if_needed()

#         if self.df is None:
#             raise RuntimeError("DataFrame not loaded")

#         return query_func(self.df.copy())


from typing import Optional, Dict, Any
import pandas as pd


class DataFrameManager:
    """
    Manages a pandas DataFrame and provides filtered views
    for downstream tools.

    Data source can be CSV, Snowflake, or injected DataFrame.
    """

    def __init__(self):
        self._df: Optional[pd.DataFrame] = None

    # ---------- Loaders (ONLY ONE USED AT A TIME) ----------

    def load_from_csv(self, file_path: str) -> None:
        """
        Load data from a CSV file into memory.
        Primary data source for POC.
        """
        self._df = pd.read_csv(file_path)

    def load_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Inject a DataFrame directly (used for tests / mocks).
        """
        self._df = df.copy()

    # def load_from_snowflake(self, connector) -> None:
    #     """
    #     Legacy / future use.
    #     Not used in current POC.
    #     """
    #     self._df = connector.fetch_dataframe()

    def load_from_snowflake(self, connector) -> None:
     raise RuntimeError(
        "Direct Snowflake access is disabled. "
        "Use CSV snapshots only."
    )

    # ---------- Core Accessors ----------

    def get_dataframe(self) -> pd.DataFrame:
        if self._df is None:
            raise ValueError("DataFrame not initialized. Load data first.")
        return self._df

    # ---------- Query Helpers (USED BY TOOLS) ----------

    def filter_dataframe(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply column=value filters.
        """
        df = self.get_dataframe()

        for column, value in filters.items():
            if column not in df.columns:
                raise ValueError(f"Invalid column: {column}")
            df = df[df[column] == value]

        return df

    def select_columns(self, columns: list[str]) -> pd.DataFrame:
        df = self.get_dataframe()

        missing = set(columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        return df[columns]

    
