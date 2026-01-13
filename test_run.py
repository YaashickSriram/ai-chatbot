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

from app.data.dataframe_manager import DataFrameManager
from app.tools.list_tool import ListTool


def main():
    # Step 1: Load CSV via DataFrameManager
    df_manager = DataFrameManager()
    df_manager.load_from_csv(
        "app/data/snapshots/G17_WFN_CONSOLIDATED_REPORT.csv"
    )

    df = df_manager.get_dataframe()

    # Step 2: Initialize ListTool
    tool = ListTool()

    # --------------------------------------------------
    # USER QUERY 3:
    # "Which initiative in 2024 under breastfeeding support
    #  contains parental leave questions?"
    # --------------------------------------------------
    params = {
        "filters": {
            "EFFECTIVE_YEAR": 2024,
            "CATEGORY": "Breastfeeding Support"
        },
        "contains": {
            "QUESTION": "parental leave"
        },
        "columns": [
            "INITIATIVE_NAME",
            "QUESTION"
        ],
        "limit": 20
    }

    result = tool.execute(df, params)

    print("ListTool Result:")
    print(f"Row count: {result['row_count']}")
    print("-" * 50)

    for record in result["records"]:
        print(record)


if __name__ == "__main__":
    main()
