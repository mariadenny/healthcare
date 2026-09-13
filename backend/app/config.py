from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    app_name: str = "Healthcare Appointment Flow Optimizer API"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "postgresql://postgres:password@localhost:5432/healthcare_db"
    secret_key: str = "development-secret-key-placeholder"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
