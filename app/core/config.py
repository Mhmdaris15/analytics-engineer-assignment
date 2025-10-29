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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
