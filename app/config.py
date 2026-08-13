import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    # LLM Settings
    OPENAI_API_KEY: str = Field(default="sk-mock-key-for-local-testing")
    MODEL_NAME: str = Field(default="gpt-4o-mini")
    TEMPERATURE: float = Field(default=0.0)

    # Database Settings
    DATABASE_URL: str = Field(default="sqlite:///./inventory.db")
    CHECKPOINTS_DB_PATH: str = Field(default="./checkpoints.sqlite")
    MAX_QUERY_ROWS: int = Field(default=100)
    QUERY_TIMEOUT_SECONDS: int = Field(default=10)

    # Security & JWT
    JWT_SECRET: str = Field(default="inventory_sql_ai_jwt_secret_key_change_in_production_987654321")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=480)

    # Observability
    LANGSMITH_API_KEY: str = Field(default="")
    LANGCHAIN_TRACING_V2: str = Field(default="false")
    LANGCHAIN_PROJECT: str = Field(default="inventory-sql-ai-chatbot")

    # App Settings
    APP_ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    CORS_ORIGINS: Union[List[str], str] = Field(default=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"])

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
