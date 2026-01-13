from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --------------------
    # Snowflake Config
    # --------------------
    SF_USER: str
    SF_PASSWORD: str
    SF_ACCOUNT: str
    SF_ROLE: str
    SF_WAREHOUSE: str
    SF_DATABASE: str
    SF_SCHEMA: str
    SF_TABLE: str

    # --------------------
    # Azure OpenAI Config (OPTIONAL)
    # --------------------
    AZ_OAI_ENDPOINT: str
    AZ_OAI_API_KEY: str
    AZ_OAI_DEPLOYMENT: str
    AZ_OAI_API_VERSION: str = "2023-07-01-preview"

    # --------------------
    # OpenAI Config (REQUIRED for fallback)
    # --------------------
    #OPENAI_API_KEY: str

    # --------------------
    # App-level
    # --------------------
    DATA_REFRESH_INTERVAL: int = 3600
    MAX_DATAFRAME_ROWS: int = 100_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings() # type: ignore[arg-type]