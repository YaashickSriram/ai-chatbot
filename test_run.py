# from app.utils.llm_client import AzureOpenAIClient


# def main():
#     client = AzureOpenAIClient()

#     messages = [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Reply with the word OK only."}
#     ]

#     print("Sending request to Azure OpenAI...\n")
#     response = client.chat(messages)

#     print("LLM Response:")
#     print(response)


# if __name__ == "__main__":
#     main()

# from app.data.dataframe_manager import DataFrameManager
# from app.tools.list_tool import ListTool


# def main():
#     # Step 1: Load CSV via DataFrameManager
#     df_manager = DataFrameManager()
#     df_manager.load_from_csv(
#         "app/data/snapshots/G17_WFN_CONSOLIDATED_REPORT.csv"
#     )

#     df = df_manager.get_dataframe()

#     # Step 2: Initialize ListTool
#     tool = ListTool()

#     # --------------------------------------------------
#     # USER QUERY 3:
#     # "Which initiative in 2024 under breastfeeding support
#     #  contains parental leave questions?"
#     # --------------------------------------------------
#     params = {
#         "filters": {
#             "EFFECTIVE_YEAR": 2024,
#             "CATEGORY": "Breastfeeding Support"
#         },
#         "contains": {
#             "QUESTION": "parental leave"
#         },
#         "columns": [
#             "INITIATIVE_NAME",
#             "QUESTION"
#         ],
#         "limit": 20
#     }

#     result = tool.execute(df, params)

#     print("ListTool Result:")
#     print(f"Row count: {result['row_count']}")
#     print("-" * 50)

#     for record in result["records"]:
#         print(record)


# if __name__ == "__main__":
#     main()

# from app.data.dataframe_manager import DataFrameManager
# from app.tools.aggregation_tool import AggregationTool


# def main():
#     # Step 1: Load CSV via DataFrameManager
#     df_manager = DataFrameManager()
#     df_manager.load_from_csv(
#         "app/data/snapshots/G17_WFN_CONSOLIDATED_REPORT.csv"
#     )

#     # Step 2: Initialize AggregationTool
#     tool = AggregationTool(df_manager)

#     # --------------------------------------------------
#     # TEST 1:
#     # "How many surveys are there?"
#     # --------------------------------------------------
#     params_1 = {
#         "operation": "count"
#     }

#     result_1 = tool.execute(params_1)

#     print("TEST 1: Total survey count")
#     print(result_1)
#     print("-" * 60)

#     # --------------------------------------------------
#     # TEST 2:
#     # "Count initiatives by year"
#     # --------------------------------------------------
#     params_2 = {
#         "operation": "count",
#         "group_by": ["EFFECTIVE_YEAR"]
#     }

#     result_2 = tool.execute(params_2)

#     print("TEST 2: Count by year")
#     for row in result_2["rows"]:
#         print(row)
#     print("-" * 60)

#     # --------------------------------------------------
#     # TEST 3:
#     # "How many surveys are there in 2024?"
#     # --------------------------------------------------
#     params_3 = {
#         "operation": "count",
#         "filters": {
#             "EFFECTIVE_YEAR": 2024
#         }
#     }

#     result_3 = tool.execute(params_3)

#     print("TEST 3: Count for 2024")
#     print(result_3)
#     print("-" * 60)


# if __name__ == "__main__":
#     main()

from app.data.dataframe_manager import DataFrameManager
from app.tools.comparison_tool import ComparisonTool

def test_comparison_tool():
    df_manager = DataFrameManager()
    df_manager.load_from_csv("data/snapshots/G17_WFN_CONSOLIDATED_REPORT.csv")

    tool = ComparisonTool()

    print("\nTEST: Compare 2023 vs 2024")
    result = tool.execute({
        "df": df_manager.get_dataframe(),
        "group_by": "EFFECTIVE_YEAR",
        "values": [2023, 2024]
    })

    print(result)

if __name__ == "__main__":
    test_comparison_tool()
