from app.agents.reAct_agents import ReActAgent
from app.tools.list_tool import ListTool
from app.tools.comparison_tool import ComparisonTool
from app.data.dataframe_manager import DataFrameManager


def test_react_agent():
    df_manager = DataFrameManager()
    tools = [
        ListTool(df_manager),
        ComparisonTool(df_manager),
    ]

    agent = ReActAgent(tools)

    question = "List all invoices from Africa"
    response = agent.run(question)

    print("Agent Response:")
    print(response)


if __name__ == "__main__":
    test_react_agent()
