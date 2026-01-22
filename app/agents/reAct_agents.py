from typing import Dict, Any
import json
import re


class ReActAgent:
    """
    ReAct-style agent that:
    - Uses LLM for intent + parameter extraction
    - Executes tools on a shared DataFrame
    """

    def __init__(self, llm_client, dataframe_manager, tools: Dict[str, Any]):
        self.llm = llm_client
        self.df_manager = dataframe_manager
        self.tools = tools

    # -----------------------------
    # TOOL SELECTION (LLM ONLY)
    # -----------------------------
    def _select_tool(self, user_query: str) -> str:
        messages = [
            {
                "role": "system",
                "content": """
You are an intent classifier for a data analytics system.

Available tools:
- direct: single numeric answers (counts, totals)
- list: list records
- aggregation: sums, averages, grouped metrics
- comparison: compare groups or periods

Rules:
- Choose exactly ONE tool
- Respond ONLY in JSON
- No explanations

JSON format:
{ "tool": "<tool_name>" }
"""
            },
            {"role": "user", "content": user_query},
        ]

        response = self.llm.chat(messages)
        # parsed = json.loads(response)

         # ✅ FIX: strip markdown + whitespace
        cleaned = response.strip()

        # Remove ```json ... ```
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^```", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)

        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"LLM returned invalid JSON:\n{response}"
            ) from e

        tool_name = parsed.get("tool")
        if tool_name not in self.tools:
            raise ValueError(f"Unsupported tool selected: {tool_name}")

        return tool_name

    # -----------------------------
    # PARAM EXTRACTION (LLM)
    # -----------------------------
    def _extract_params(self, tool_name: str, user_query: str) -> Dict[str, Any]:
        messages = [
            {
                "role": "system",
                "content": f"""
You extract structured parameters for the tool: {tool_name}

Respond ONLY in JSON.
"""
            },
            {"role": "user", "content": user_query},
        ]

        response = self.llm.chat(messages)

        cleaned = response.strip()

        # Remove ```json ... ```
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^```", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)

        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            return parsed
        except json.JSONDecodeError as e:
            raise ValueError(
                f"LLM returned invalid JSON:\n{response}"
            ) from e
        

    # -----------------------------
    # EXECUTION
    # -----------------------------
    def run(self, user_query: str) -> Dict[str, Any]:
        tool_name = self._select_tool(user_query)
        params = self._extract_params(tool_name, user_query)

        tool = self.tools[tool_name]
        df = self.df_manager.get_dataframe()

        return tool.execute(df=df, params=params)
