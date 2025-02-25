from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_AISTUDIO_API_KEY: str
    FIRECRAWL_API_KEY: str

    # Service Configuration
    API_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"

    # Database Configuration
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Browser Configuration
    USE_DEFAULT_BROWSER: bool = False
    SELENIUM_BROWSER: str = "chrome"

    # Logging Configuration
    LOG_LEVEL: str = "info"
    LOG_FILE: str = "backend.log"

    # Security
    JWT_SECRET: str
    ENCRYPTION_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Performance
    MAX_CONCURRENT_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 30000

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 