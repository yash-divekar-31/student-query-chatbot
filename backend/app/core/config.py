from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Student Query Chatbot API"
    app_version: str = "0.1.0"
    model_dir: Path = BACKEND_DIR / "models"
    dataset_path: Path = BACKEND_DIR / "data" / "intents.json"
    confidence_threshold: float = 0.065
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
