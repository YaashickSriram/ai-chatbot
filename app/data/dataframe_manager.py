import os
import pandas as pd
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
import logging

from app.data.snowflake_connector import SnowflakeConnector
from app.config import settings


class DataFrameManager:
    """
    Manages loading, caching, refreshing, and safe access
    to an in-memory Pandas DataFrame sourced from Snowflake.
    """

    def __init__(self, snowflake_connector: SnowflakeConnector):
        self.connector = snowflake_connector
        self.df: Optional[pd.DataFrame] = None
        self.last_refresh: Optional[datetime] = None

    def load_data(self, table_name: Any = settings.SF_TABLE):
        """
        Load data from Snowflake into the DataFrame.
        """

        query = f"SELECT * FROM {table_name}"

        self.df = self.connector.fetch_data(query)
        self.last_refresh = datetime.now() # will refresh the data every time fetch_data() is called so needed timestamp of last refresh

        self._preprocess_data()

    def _preprocess_data(self):
        """
        Preprocess DataFrame (handle dates, nulls, types).
        """
        if self.df is None:
            return "Dataframe has NONE"

        # Convert date-like columns to datetime
        object_columns = self.df.select_dtypes(include=["object"]).columns
        for col in object_columns:
            if "date" in col.lower(): #use regex
                self.df[col] = pd.to_datetime(self.df[col], errors="coerce")

        # Placeholder for future preprocessing
        # (null handling, normalization, etc.)

    def refresh_if_needed(self):
        """
        Refresh data if cache is older than configured threshold.
        """
        if (
            self.last_refresh is None or
            datetime.now() - self.last_refresh >
            timedelta(seconds=settings.DATA_REFRESH_INTERVAL)
        ):
            self.load_data()

    def get_dataframe(self) -> pd.DataFrame:
        """
        Return a safe copy of the cached DataFrame.
        """
        self.refresh_if_needed()

        if self.df is None:
            raise RuntimeError("DataFrame not loaded")

        return self.df.copy()

    def execute_query(self, query_func: Callable[[pd.DataFrame], pd.DataFrame]) -> pd.DataFrame:
        """
        Execute a Pandas query function safely on the DataFrame.
        """
        self.refresh_if_needed()

        if self.df is None:
            raise RuntimeError("DataFrame not loaded")

        return query_func(self.df.copy())
