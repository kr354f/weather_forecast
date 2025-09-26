"""Configuration management for the weather service."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    openweathermap_api_key: str = ""
    openweathermap_base_url: str = "https://api.openweathermap.org/data/2.5"
    
    # Application Configuration
    app_name: str = "Weather Forecast Microservice"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8080
    
    # Request Configuration
    request_timeout: int = 10
    max_concurrent_requests: int = 100
    
    # Caching (for future implementation)
    cache_ttl: int = 300  # 5 minutes
    
    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def validate_settings() -> bool:
    """Validate that all required settings are configured."""
    if not settings.openweathermap_api_key:
        return False
    return True


def get_api_key() -> Optional[str]:
    """Get OpenWeatherMap API key from environment or settings."""
    # Try environment variable first
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if api_key:
        return api_key
    
    # Fallback to settings
    return settings.openweathermap_api_key if settings.openweathermap_api_key else None