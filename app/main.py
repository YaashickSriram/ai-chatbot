from fastapi import FastAPI

from app.data.snowflake_connector import SnowflakeConnector
from app.data.dataframe_manager import DataFrameManager

from app.tools.list_tool import ListTool
from app.tools.aggregation_tool import AggregationTool
from app.tools.comparison_tool import ComparisonTool
from app.tools.direct_query_tool import DirectQueryTool

from app.agents.reAct_agents import ReActAgent


app = FastAPI()

_snowflake_connector: SnowflakeConnector | None = None
_dataframe_manager: DataFrameManager | None = None
_agent: ReActAgent | None = None


def initialize_app() -> None:
    """
    Initializes data layer, tools, and agent.
    """
    global _snowflake_connector, _dataframe_manager, _agent

    _snowflake_connector = SnowflakeConnector()
    _dataframe_manager = DataFrameManager(_snowflake_connector)
    _dataframe_manager.load_data()

    tools = {
        "list_tool": ListTool(_dataframe_manager),
        "aggregation_tool": AggregationTool(_dataframe_manager),
        "comparison_tool": ComparisonTool(_dataframe_manager),
        "direct_query_tool": DirectQueryTool(_dataframe_manager),
    }

    _agent = ReActAgent(tools)


def get_agent() -> ReActAgent:
    """
    Safe accessor for the initialized agent.
    """
    if _agent is None:
        raise RuntimeError("Agent not initialized. Call initialize_app() first.")

    return _agent

def get_dataframe_manager() -> DataFrameManager:
    """
    Safe accessor for the initialized DataFrameManager.
    """
    if _dataframe_manager is None:
        raise RuntimeError("DataFrameManager not initialized. Call initialize_app() first.")

    return _dataframe_manager



@app.on_event("startup")
def startup_event():
    initialize_app()
    print("✅ Startup complete: Data, Tools, and Agent initialized")
