from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Student Query Chatbot API"
    app_version: str = "0.1.0"
    model_dir: Path = BACKEND_DIR / "models"
    dataset_path: Path = BACKEND_DIR / "data" / "intents.json"
    confidence_threshold: float = 0.065
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            origins = [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]
        elif isinstance(value, list):
            origins = [
                origin.strip() if isinstance(origin, str) else origin
                for origin in value
                if not isinstance(origin, str) or origin.strip()
            ]
        else:
            return value

        if "*" in origins:
            raise ValueError("Wildcard CORS origins are not allowed.")
        return origins

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
