# from typing import Dict, Any, Tuple

# from app.tools.base_tool import BaseTool


# class ReActAgent:
#     """
#     ReAct-style agent that orchestrates reasoning and tool execution.
#     This version contains NO LLM logic yet (manual reasoning only).
#     """

#     def __init__(self, tools: Dict[str, BaseTool]):
#         self.tools = tools

#     def handle_query(self, user_query: str) -> Dict[str, Any]:
#         """
#         Entry point for handling a user question.
#         """
#         # Step 1: Reason about the query (manual logic for POC)
#         tool_name, tool_params = self._reason(user_query)

#         # Step 2: Execute the selected tool
#         result = self._execute_tool(tool_name, tool_params)

#         # Step 3: Format the final response
#         return self._format_response(user_query, result)

#     def _reason(self, user_query: str) -> Tuple[str, Dict[str, Any]]:
#         """
#         Analyze the user query and decide:
#         - which tool to use
#         - what parameters to pass

#         NOTE:
#         This is MANUAL reasoning for POC.
#         It will be replaced by LLM-based reasoning later.
#         """
#         query = user_query.lower()

#         # Example:
#         # "What is the classification level of Notse_T1_Plant6?"
#         if "classification level" in query:
#             return "direct_query_tool", {
#                 "column": "CLASSIFICATION_LEVEL",
#                 "filters": {
#                     "INITIATIVE_NAME": "Notse_T1_Plant6"
#                 }
#             }

#         raise ValueError("Unable to determine intent from query")

#     def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Execute the selected tool with parameters.
#         """
#         tool = self.tools.get(tool_name)

#         if tool is None:
#             raise ValueError(f"Tool '{tool_name}' not registered")

#         return tool.execute(params)

#     def _format_response(
#         self,
#         user_query: str,
#         tool_result: Dict[str, Any]
#     ) -> Dict[str, Any]:
#         """
#         Convert tool output into a final structured response.
#         """
#         return {
#             "question": user_query,
#             "answer": tool_result
#         }

from typing import Dict, Any, List

from app.utils.llm_client import AzureOpenAIClient
from app.tools.base_tool import BaseTool


class ReActAgent:
    """
    POC ReAct Agent:
    - Uses LLM to decide which tool to call
    - Executes tool
    - Returns final answer
    """

    def __init__(self, tools: List[BaseTool]):
        self.llm = AzureOpenAIClient()
        self.tools = {tool.name: tool for tool in tools}

    def run(self, user_question: str) -> str:
        """
        Entry point for agent reasoning.
        """

        # 1️⃣ Ask LLM which tool to use
        tool_prompt = self._build_tool_selection_prompt(user_question)
        tool_decision = self.llm.chat(tool_prompt)

        # POC assumption: LLM returns tool name only
        tool_name = tool_decision.strip()

        if tool_name not in self.tools:
            return f"No suitable tool found for question: {user_question}"

        # 2️⃣ Execute tool
        tool = self.tools[tool_name]
        tool_result = tool.execute({"question": user_question})

        # 3️⃣ Ask LLM to generate final answer
        final_prompt = self._build_final_answer_prompt(
            user_question, tool_result
        )
        final_answer = self.llm.chat(final_prompt)

        return final_answer

    def _build_tool_selection_prompt(self, question: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "You are a classifier. "
                    "Based on the user question, respond with ONLY one tool name "
                    "from this list: list_tool, comparison_tool."
                ),
            },
            {"role": "user", "content": question},
        ]

    def _build_final_answer_prompt(
        self, question: str, observation: Any
    ) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "You are a data analyst. Use the observation to answer.",
            },
            {"role": "user", "content": f"Question: {question}"},
            {"role": "assistant", "content": f"Observation: {observation}"},
        ]
