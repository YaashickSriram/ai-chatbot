import pandas as pd
from datetime import datetime
from app.data.dataframe_manager import DataFrameManager


def load_csv_for_testing(
    dataframe_manager: DataFrameManager,
    csv_path: str
) -> None:
    """
    TEST ONLY:
    Load CSV data directly into DataFrameManager
    and prevent refresh from Snowflake.
    """
    dataframe_manager.df = pd.read_csv(csv_path)

    # ✅ Mark data as freshly loaded
    dataframe_manager.last_refresh = datetime.now()