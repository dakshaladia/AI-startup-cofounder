"""
Configuration management for the AI Startup Co-Founder backend service.
"""

import os
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/startup_cofounder"
    TEST_DATABASE_URL: str = "postgresql://user:password@localhost:5432/startup_cofounder_test"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Vector Database
    VECTOR_DB_TYPE: str = "faiss"  # faiss, pinecone, weaviate
    VECTOR_DB_PATH: str = "./data/faiss_index"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "startup-cofounder"
    WEAVIATE_URL: str = "http://localhost:8080"
    WEAVIATE_API_KEY: Optional[str] = None
    
    # LLM Configuration
    GEMINI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-1.5-pro"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4000
    LOCAL_LLM_URL: str = "http://localhost:11434"
    LOCAL_LLM_MODEL: str = "llama2"
    
    # Embedding Configuration
    TEXT_EMBEDDING_MODEL: str = "text-embedding-004"
    TEXT_EMBEDDING_DIMENSION: int = 768
    IMAGE_EMBEDDING_MODEL: str = "clip-vit-base-patch32"
    IMAGE_EMBEDDING_DIMENSION: int = 512
    
    # Ingestion Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    OCR_PROVIDER: str = "tesseract"
    OCR_LANGUAGE: str = "eng"
    IMAGE_MAX_SIZE: int = 1024
    IMAGE_QUALITY: int = 85
    
    # Evaluation Settings
    MARKET_SIGNAL_WEIGHT: float = 0.3
    FEASIBILITY_WEIGHT: float = 0.25
    NOVELTY_WEIGHT: float = 0.25
    CRITIC_SEVERITY_WEIGHT: float = 0.2
    NOVELTY_THRESHOLD: float = 0.7
    VISUAL_NOVELTY_THRESHOLD: float = 0.6
    
    # Security
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Development
    AUTO_RELOAD: bool = True
    MOCK_LLM: bool = False
    MOCK_EMBEDDINGS: bool = False
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("DEBUG", pre=True)
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return v
    
    @validator("AUTO_RELOAD", pre=True)
    def parse_auto_reload(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return v
    
    @validator("ENABLE_METRICS", pre=True)
    def parse_enable_metrics(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return v
    
    @validator("MOCK_LLM", pre=True)
    def parse_mock_llm(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return v
    
    @validator("MOCK_EMBEDDINGS", pre=True)
    def parse_mock_embeddings(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
