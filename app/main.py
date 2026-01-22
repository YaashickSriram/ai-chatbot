from fastapi import FastAPI

from app.api.routes import router
from app.agents.reAct_agents import ReActAgent
from app.data.dataframe_manager import DataFrameManager
from app.tools.direct_query_tool import DirectQueryTool
from app.tools.list_tool import ListTool
from app.tools.aggregation_tool import AggregationTool
from app.tools.comparison_tool import ComparisonTool
from app.utils.llm_client import AzureOpenAIClient

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="Chatbot Pandas API",
    version="1.0.0",
    description="ReAct-based data analytics agent"
)

# -------------------------------------------------
# SINGLETON BOOTSTRAP (CRITICAL DESIGN)
# -------------------------------------------------

# Load dataset once
df_manager = DataFrameManager()
df_manager.load_from_csv(
    "app/data/snapshots/G17_WFN_CONSOLIDATED_REPORT.csv"
)

# Azure OpenAI client
llm_client = AzureOpenAIClient()

# Tools (stateless)
tools = {
    "direct": DirectQueryTool(),
    "list": ListTool(),
    "aggregation": AggregationTool(),
    "comparison": ComparisonTool(),
}

# Core agent
agent = ReActAgent(
    llm_client=llm_client,
    dataframe_manager=df_manager,
    tools=tools,
)

# Mount API routes
app.include_router(router)

# -------------------------------------------------
# TEMP Health Check (Phase 4.1 only)
# -------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "agent": "ready",
        "tools": list(tools.keys())
    }
