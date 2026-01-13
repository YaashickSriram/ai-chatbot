import snowflake.connector
import pandas as pd
from typing import Optional
from app.config import settings


class SnowflakeConnector:
    def __init__(self):
        self.connection: Optional[snowflake.connector.SnowflakeConnection] = None

    def connect(self) -> None:
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

        if self.connection is None:
            raise RuntimeError("Snowflake connection not initialized")

        cursor = self.connection.cursor()
        try:
            cursor.execute(query)

            # ✅ Fetch data
            df = cursor.fetch_pandas_all()

            # ✅ Force column materialization (CRITICAL)
            df = df.copy()

            print(f"Rows fetched from Snowflake: {len(df)}")
            print(f"Columns fetched: {list(df.columns)}")

            if df.empty:
                raise RuntimeError("Snowflake query returned no data")

            return df

        finally:
            cursor.close()

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
