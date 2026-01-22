import os
import pytest

from app.agents.reAct_agents import ReActAgent
from app.data.dataframe_manager import DataFrameManager
from app.tools.direct_query_tool import DirectQueryTool
from app.tools.list_tool import ListTool
from app.tools.aggregation_tool import AggregationTool
from app.tools.comparison_tool import ComparisonTool
from app.utils.llm_client import AzureOpenAIClient


# -------------------------------------------------------------------
# FIXTURE: DataFrameManager (CSV snapshot)
# -------------------------------------------------------------------
@pytest.fixture(scope="session")
def df_manager():
    manager = DataFrameManager()
    manager.load_from_csv(
        "app/data/snapshots/G17_WFN_CONSOLIDATED_REPORT.csv"
    )
    return manager


# -------------------------------------------------------------------
# FIXTURE: Azure OpenAI client (REAL)
# -------------------------------------------------------------------
@pytest.fixture(scope="session")
def llm_client():
    return AzureOpenAIClient()


# -------------------------------------------------------------------
# FIXTURE: ReAct Agent (REAL LLM + REAL DATA)
# -------------------------------------------------------------------

@pytest.fixture(scope="session")
def agent(df_manager, llm_client):
    tools = {
        "direct":DirectQueryTool(),
        "list": ListTool(),
        "aggregation": AggregationTool(),
        "comparison": ComparisonTool(),
    }

    return ReActAgent(
        llm_client=llm_client,
        dataframe_manager=df_manager,
        tools=tools,
    )



# -------------------------------------------------------------------
# TEST 1: Tool selection → DIRECT
# -------------------------------------------------------------------
def test_direct_query_tool_selection(agent):
    query = "How many surveys are currently present?"

    tool_name = agent._select_tool(query)

    assert tool_name == "direct"


# -------------------------------------------------------------------
# TEST 2: Tool selection → LIST
# -------------------------------------------------------------------
def test_list_tool_selection(agent):
    query = (
        "Which initiative in 2024 under breastfeeding support "
        "contains parental leave questions?"
    )

    tool_name = agent._select_tool(query)

    assert tool_name == "list"


# -------------------------------------------------------------------
# TEST 3: Tool selection → AGGREGATION
# -------------------------------------------------------------------
def test_aggregation_tool_selection(agent):
    query = "Show the total number of records grouped by year"

    tool_name = agent._select_tool(query)

    assert tool_name == "aggregation"


# -------------------------------------------------------------------
# TEST 4: End-to-end execution (LIST)
# -------------------------------------------------------------------
def test_list_tool_execution(agent):
    query = (
        "Can you show me breastfeeding initiatives that had anything to do with parental leave?"
    )

    response = agent.run(query)

    assert isinstance(response, dict)
    assert response.get("tool") == "list"
    assert "results" in response
    assert isinstance(response["results"], list)
    assert len(response["results"]) > 0
