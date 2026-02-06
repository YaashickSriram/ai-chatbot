from typing import Dict, Any
import json
import re


class ReActAgent:
    """
    ReAct-style agent that:
    - Uses LLM for semantic tool planning
    - Grounds decisions in actual dataframe schema
    - Executes tools deterministically
    - Generates human-readable answers
    """

    def __init__(self, llm_client, dataframe_manager, tools: Dict[str, Any]):
        self.llm = llm_client
        self.df_manager = dataframe_manager
        self.tools = tools

    # -------------------------------------------------
    # SEMANTIC TOOL PLANNING PROMPT (CORE OF PHASE 5.3)
    # -------------------------------------------------
    def _tool_planning_prompt(self, query: str, columns: list[str]) -> str:
        cols = ", ".join(columns)
        return f"""
You are a data analytics reasoning engine.

You have access to a dataset with the following columns:
{cols}

Your task:
1. Understand the user's intent (natural language, conversational)
2. Decide the correct analytical tool
3. Extract the required parameters grounded in the dataset

Rules:
- You MUST choose columns only from the list above
- NEVER invent column names
- NEVER use conceptual words like "stage", "maturity", "doing well"
- If the question cannot be answered using these columns, return:

{{
  "tool": "none",
  "params": {{}}
}}

Available tools:

1. aggregation  
Used when the user asks about quantities, totals, averages, distributions,
comparisons across groups or time.

Required JSON format:
{{
  "tool": "aggregation",
  "params": {{
    "operation": "count | sum | average",
    "group_by": "<column name>",
    "column": "<numeric column name or null>"
  }}
}}

Rules for aggregation:
- Use "count" for how many, number of, volume, prevalence
- Use "sum" for total, combined, overall amount
- Use "average" for mean or typical value
- column MUST be null for count
- group_by MUST be one of the provided columns

2. list  
Used when the user wants to see records, initiatives, examples, details,
policies, questions, or descriptions.

Required JSON format:
{{
  "tool": "list",
  "params": {{
    "filters": {{
      "<column name>": "<value>"
    }},
    "contains": {{
      "<column name>": "<substring>"
    }},
    "columns": ["<column name>", "..."],
    "distinct": true,
    "limit": 50
  }}
}}

Rules for list:
- Infer semantic meaning (e.g. "support for new mothers" → CATEGORY = "Breastfeeding Support")
- Use columns only from the provided list
- Use "contains" for partial matches, locations, or city names (e.g. "in Dubai")
- Prefer location-related columns: SITE_NAME, SITE_COUNTRY, COUNTRY, SITE_REGION, ENTITY, PLANT
- If user asks for "initiative names", set columns=["INITIATIVE_NAME"] and distinct=true
- Values do NOT need exact string match but must be semantically correct

STRICT RULES:
- Respond ONLY with valid JSON
- DO NOT explain anything
- DO NOT invent column names
- If something cannot be inferred, set it explicitly to null

User query:
{query}
"""

    # -------------------------------------------------
    # PLAN: TOOL + PARAMS (LLM-ONLY, SCHEMA-GROUNDED)
    # -------------------------------------------------
    def plan(self, user_query: str) -> Dict[str, Any]:
        df = self.df_manager.get_dataframe()
        prompt = self._tool_planning_prompt(
            query=user_query,
            columns=df.columns.tolist()
        )

        response = self.llm.chat([
            {"role": "system", "content": prompt}
        ])

        cleaned = response.strip()
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^```", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            plan = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON:\n{response}") from e

        if "tool" not in plan or "params" not in plan:
            raise ValueError("Invalid tool plan structure returned by LLM")

        return plan

    # -------------------------------------------------
    # EXECUTION (DETERMINISTIC)
    # -------------------------------------------------
    def run(self, user_query: str) -> Dict[str, Any]:
        plan = self.plan(user_query)

        df = self.df_manager.get_dataframe()
        schema = list(df.columns)

        tool_name = plan["tool"]
        params = plan["params"]

        if tool_name == "none":
            return {
            "tool": "none",
            "results": [],
            "value": None
        }
    
        if tool_name not in self.tools:
            raise ValueError(f"Unsupported tool selected: {tool_name}")

        tool = self.tools[tool_name]
        df = self.df_manager.get_dataframe()

        return tool.execute(df=df, params=params)
        
        plan = self.plan(user_query)
        if plan["tool"] == "none":
            return self._clarify(user_query, df.columns.tolist())

    
    def _clarify(self, query: str, columns: list[str]) -> Dict[str, Any]:
        return {
        "tool": "none",
        "answer": (
            "I can’t answer this directly using the available data. "
            "You can ask about initiatives by location, category, "
            "classification level, company, or year."
        ),
        "results": None,
        "value": None
    }


    # -------------------------------------------------
    # ANSWER GENERATION (NLP RESPONSE LAYER)
    # -------------------------------------------------
    def generate_answer(self, query: str, tool_response: dict) -> str:
        results = tool_response.get("results") or []
        if not results:
            return (
            "The dataset does not contain enough information "
            "to answer this question."
        )
        messages = [
        {
            "role": "system",
            "content": """
You are a data assistant.

STRICT RULES:
- Use ONLY the data provided below
- DO NOT use external knowledge
- DO NOT infer meaning beyond the data
- If something is not in the data, say so clearly
"""
        },
        {
            "role": "user",
            "content": f"""
        User question: {query}
        Data:
        {json.dumps(results, indent=2)}

Task:
- Answer in plain English
- Summarize only what is visible in the data
"""
        }
    ]
        response = self.llm.chat(messages)
        return response.strip()
