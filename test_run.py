from app.utils.llm_client import AzureOpenAIClient


def main():
    client = AzureOpenAIClient()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Reply with the word OK only."}
    ]

    print("Sending request to Azure OpenAI...\n")
    response = client.chat(messages)

    print("LLM Response:")
    print(response)


if __name__ == "__main__":
    main()
