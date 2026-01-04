import os
from typing import List, Dict

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.config import settings

load_dotenv()


class AzureOpenAIClient:
    """
    Thin wrapper over Azure OpenAI Chat Completions.
    """

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZ_OAI_API_KEY"),
            api_version=os.getenv("AZ_OAI_API_VERSION"),
            azure_endpoint= settings.AZ_OAI_ENDPOINT
        )
        self.deployment_name = os.getenv("AZ_OAI_DEPLOYMENT")

    def chat(self, messages) -> str:
        """
        Send messages to Azure OpenAI and return assistant response text.
        """
        response = self.client.chat.completions.create(
            model= self.deployment_name,   # ✅ gpt-4o (deployment name) # type: ignore
            messages=messages,
            temperature=0.0,
        )

        return response.choices[0].message.content # type: ignore
