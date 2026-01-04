import snowflake.connector
import pandas as pd
from typing import Optional
from app.config import settings


class SnowflakeConnector:
    def __init__(self):
        self.connection: Optional[snowflake.connector.SnowflakeConnection] = None

    def connect(self) -> None:
        """
        Establish a Snowflake connection if not already connected.
        """
        if self.connection is None:
            self.connection = snowflake.connector.connect(
                user=settings.SF_USER,
                password=settings.SF_PASSWORD,
                account=settings.SF_ACCOUNT,
                role=settings.SF_ROLE,
                warehouse=settings.SF_WAREHOUSE,
                database=settings.SF_DATABASE,
                schema=settings.SF_SCHEMA,
            )
    def fetch_data(self, query: str) -> pd.DataFrame:
        self.connect()
        # ✅ Explicit guard for type checker
        if self.connection is None:
            raise RuntimeError("Snowflake connection not initialized")
        conn = self.connection  # local non-optional reference
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            df = cursor.fetch_pandas_all()
        finally:
            cursor.close()
        if df is None or df.empty:
            raise RuntimeError("Snowflake query returned no data")
        return df
        
    def close(self) -> None:
        """
        Close Snowflake connection.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None
