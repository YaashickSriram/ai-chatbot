import json
from typing import Dict, Any

from app.data.dataframe_manager import DataFrameManager
from app.tools.base_tool import BaseTool
from app.utils.llm_client import AzureOpenAIClient


class ReActAgent:
    """
    ReAct Agent (POC-level, LLM-only).

    Flow:
    1. Use LLM to reason and select the correct tool (intent classification)
    2. Execute the selected tool on pandas DataFrame
    3. Use LLM to generate a final human-readable response
    """

    def __init__(
        self,
        llm_client: AzureOpenAIClient,
        dataframe_manager: DataFrameManager,
        tools: Dict[str, BaseTool],
    ):
        if llm_client is None:
            raise ValueError("ReActAgent requires a valid LLM client")

        self.llm = llm_client
        self.df_manager = dataframe_manager
        self.tools = tools

    # ------------------------------------------------------------------
    # STEP 1: LLM-BASED TOOL SELECTION (NO KEYWORDS, NO MOCKS)
    # ------------------------------------------------------------------
    def _select_tool(self, user_query: str) -> str:
        """
        Uses LLM to determine the correct tool for the given user query.
        """

        system_prompt = """
You are an intent classifier for a data analytics system.

Available tools:
- direct: single numeric answers (counts, totals)
- list: returning multiple records
- comparison: comparing groups or time periods
- aggregation: averages, sums, grouped metrics

Rules:
- Choose exactly ONE tool
- Respond ONLY in valid JSON
- No explanation, no extra text
- If unsure, choose the MOST LIKELY tool

JSON format:
{
  "tool": "<tool_name>"
}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]

        response = self.llm.chat(messages)

        try:
            parsed = json.loads(response)
            tool_name = parsed["tool"]
        except Exception as exc:
            raise RuntimeError(
                f"Failed to parse LLM tool selection response: {response}"
            ) from exc

        if tool_name not in self.tools:
            raise ValueError(f"LLM selected unknown tool: {tool_name}")

        return tool_name

    # ------------------------------------------------------------------
    # STEP 2: TOOL EXECUTION
    # ------------------------------------------------------------------
    def _execute_tool(self, tool_name: str, user_query: str) -> Dict[str, Any]:
        """
        Executes the selected tool using pandas DataFrame.
        """

        tool = self.tools[tool_name]
        df = self.df_manager.get_dataframe()

        return tool.execute(
            {
                "query": user_query,
                "df": df,
            }
        )

    # ------------------------------------------------------------------
    # STEP 3: FINAL LLM RESPONSE GENERATION
    # ------------------------------------------------------------------
    def _generate_final_answer(
        self,
        user_query: str,
        tool_name: str,
        tool_result: Dict[str, Any],
    ) -> str:
        """
        Converts tool output into a natural language answer using LLM.
        """

        messages = [
            {
                "role": "system",
                "content": "You are a helpful data assistant. Answer clearly and concisely.",
            },
            {
                "role": "user",
                "content": f"""
User Query:
{user_query}

Tool Used:
{tool_name}

Tool Output:
{json.dumps(tool_result, indent=2)}

Generate a clear, human-friendly response.
""",
            },
        ]

        return self.llm.chat(messages)

    # ------------------------------------------------------------------
    # PUBLIC ENTRY POINT
    # ------------------------------------------------------------------
    def run(self, user_query: str) -> str:
        """
        Full ReAct loop execution.
        """

        tool_name = self._select_tool(user_query)
        tool_result = self._execute_tool(tool_name, user_query)
        final_answer = self._generate_final_answer(
            user_query, tool_name, tool_result
        )

        return final_answer
