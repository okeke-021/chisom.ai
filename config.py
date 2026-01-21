"""Configuration management for Chisom.ai"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    mistral_api_key: str
    langsmith_api_key: str
    github_token: str
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Auth
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    
    # Langsmith
    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_project: str = "chisom-ai-builder"
    
    # Chainlit
    chainlit_auth_secret: str
    chainlit_url: str = "http://localhost:8000"
    
    # Rate Limits
    free_tier_daily_limit: int = 5
    pro_tier_daily_limit: int = 30
    pro_tier_price: int = 29
    
    # Docker
    docker_host: str = "unix:///var/run/docker.sock"
    
    # App Config
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
