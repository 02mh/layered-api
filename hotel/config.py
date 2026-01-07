"""
Uses Pydantic settings to load configuration from environment variables
with standard defaults for development.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = "sqlite:///hotel.db"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Application Configuration
    app_name: str = "Hotel Management API"
    debug: bool = False

    # Rate Limiting Configuration
    rate_limit_enabled: bool = True
    rate_limit_storage: str = "memory://"
    rate_limit_read: str = "100/minute"
    rate_limit_write: str = "20/minute"
    rate_limit_delete: str = "10/minute"
    rate_limit_search: str = "50/minute"
    rate_limit_whitelist: str = "127.0.0.1,::1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
