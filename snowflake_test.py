# # from app.data.snowflake_connector import SnowflakeConnector

# # conn = SnowflakeConnector()

# # df = conn.fetch_data("SELECT * FROM G17_WFN_CONSOLIDATED_REPORT LIMIT 10")

# # print(df.head())
# # print(df.columns)
# # print("Row count:", len(df))

# from app.data.snowflake_connector import SnowflakeConnector
# from app.data.dataframe_manager import DataFrameManager

# connector = SnowflakeConnector()
# df_manager = DataFrameManager(connector)

# df_manager.load_data()
# df = df_manager.get_dataframe()

# print(df.head())
# print("Rows:", len(df))

from app.data.snowflake_connector import SnowflakeConnector
from app.data.dataframe_manager import DataFrameManager

connector = SnowflakeConnector()
df_manager = DataFrameManager(connector)

# Load data from Snowflake
df_manager.load_data()

# Retrieve dataframe
df = df_manager.get_dataframe()

print(df.head())
print("Rows:", len(df))
print("Columns:", df.columns)
