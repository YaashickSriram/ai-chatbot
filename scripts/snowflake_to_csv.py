"""
POC Snowflake → CSV exporter

Purpose:
- Pull data from Snowflake
- Store as CSV snapshot for offline analytics
- Decoupled from application runtime
"""

import os
from pathlib import Path
import pandas as pd

from app.data.snowflake_connector import SnowflakeConnector


class SnowflakeCSVExporter:
    def __init__(self, output_dir: str = "app/data/snapshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_table(
        self,
        table_name: str,
        csv_name: str | None = None,
    ) -> str:
        """
        Fetch full Snowflake table and write CSV.

        Returns:
            Path to generated CSV file
        """
        connector = SnowflakeConnector()

        try:
            print(f"Connecting to Snowflake...")
            df = connector.fetch_data(f"SELECT * FROM {table_name}")
            
            if df.empty:
                raise RuntimeError("Snowflake query returned no data")

            csv_file = csv_name or f"{table_name}.csv"
            output_path = self.output_dir / csv_file

            df.to_csv(output_path, index=False)
            print(f"CSV written to: {output_path}")

            return str(output_path)

        finally:
            connector.close()


if __name__ == "__main__":
    """
    Manual execution entry point
    """
    TABLE_NAME = "G17_WFN_CONSOLIDATED_REPORT"

    exporter = SnowflakeCSVExporter()
    exporter.export_table(TABLE_NAME)
