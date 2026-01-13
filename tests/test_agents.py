import pytest

from app.agents.reAct_agents import ReActAgent
from app.data.dataframe_manager import DataFrameManager
from app.tools.direct_query_tool import DirectQueryTool
from app.tools.list_tool import ListTool
from app.tools.comparison_tool import ComparisonTool
from app.tools.aggregation_tool import AggregationTool
from app.utils.llm_client import AzureOpenAIClient


@pytest.fixture(scope="session")
def agent():
    """
    Creates a real ReActAgent using:
    - Real Azure OpenAI LLM
    - CSV-backed DataFrameManager
    - Real tool implementations
    """

    # Initialize DataFrameManager (CSV mode)
    df_manager = DataFrameManager()
    df_manager.load_from_csv("G17_WFN_CONSOLIDATED_REPORT.csv")

    # Initialize tools (each owns the DataFrameManager)
    tools = {
        "direct": DirectQueryTool(df_manager),
        "list": ListTool(df_manager),
        "comparison": ComparisonTool(df_manager),
        "aggregation": AggregationTool(df_manager),
    }

    # Initialize REAL LLM client (no mocks)
    llm_client = AzureOpenAIClient()

    return ReActAgent(
        llm_client=llm_client,
        dataframe_manager=df_manager,
        tools=tools,
    )


# ------------------------------------------------------------------
# TEST 1: DIRECT QUERY (COUNT / TOTAL)
# ------------------------------------------------------------------
def test_direct_query_tool(agent):
    query = "How many surveys are in the database?"

    # Run full ReAct loop
    response = agent.run(query)

    # Assertions (LLM-safe)
    assert isinstance(response, str)
    assert len(response) > 0


# ------------------------------------------------------------------
# TEST 2: LIST INTENT (MULTIPLE RECORDS)
# ------------------------------------------------------------------
def test_list_tool(agent):
    query = "Show me the surveys conducted in 2025"

    response = agent.run(query)

    assert isinstance(response, str)
    assert len(response) > 0


# ------------------------------------------------------------------
# TEST 3: AGGREGATION INTENT
# ------------------------------------------------------------------
def test_aggregation_tool(agent):
    query = "What is the average number of surveys by department?"

    response = agent.run(query)

    assert isinstance(response, str)
    assert len(response) > 0


# ------------------------------------------------------------------
# TEST 4: COMPARISON INTENT
# ------------------------------------------------------------------
def test_comparison_tool(agent):
    query = "Compare surveys conducted in Q1 versus Q2"

    response = agent.run(query)

    assert isinstance(response, str)
    assert len(response) > 0
