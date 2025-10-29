"""
Configuration management using Pydantic Settings.
Loads environment variables and provides type-safe configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application Settings
    app_name: str = "Analytics Engineer API"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Configuration
    database_type: Literal["json", "mongodb"] = "json"
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "analytics_engineer"
    mongodb_collection: str = "invoices"
    
    # JSON Storage Configuration
    json_storage_path: str = "./data/invoices.json"
    
    # Data Generation Settings
    min_invoices_per_request: int = 2
    max_invoices_per_request: int = 5
    inconsistency_rate: float = 0.3  # 30% chance of inconsistencies
    duplicate_rate: float = 0.1  # 10% chance of duplicates
    
    # Security Settings
    secret_key: str = "your-secret-key-change-this-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    enable_auth: bool = True  # Set to True to enable authentication
    valid_api_keys: list = ["demo-api-key-12345", "test-key-67890", 'HdHKzb6LbVsGtIJU1wKWM5e3o3XTTYaL']  # Pre-shared API keys
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
