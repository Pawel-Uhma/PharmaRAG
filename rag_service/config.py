"""
Configuration file for PharmaRAG Service
Centralizes all cache, performance, and service settings
"""

import os
from pathlib import Path
from typing import Optional

# Environment variables with defaults
class Config:
    # API Configuration
    API_KEY: Optional[str] = os.getenv("API_KEY")
    MODEL: str = os.getenv("MODEL", "gpt-4o-mini")
    
    # Service Configuration
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "chroma")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Cache Configuration
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL_MINUTES: int = int(os.getenv("CACHE_TTL_MINUTES", "10"))
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    # Health Check Configuration
    HEALTH_CHECK_CACHE_THRESHOLD: float = float(os.getenv("HEALTH_CHECK_CACHE_THRESHOLD", "0.8"))
    HEALTH_CHECK_RESPONSE_TIME_THRESHOLD_MS: int = int(os.getenv("HEALTH_CHECK_RESPONSE_TIME_THRESHOLD_MS", "1000"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration values"""
        if not cls.API_KEY:
            return False
        return True
    
    @classmethod
    def get_cache_config(cls) -> dict:
        """Get cache configuration as dictionary"""
        return {
            "enabled": cls.ENABLE_CACHE,
            "ttl_minutes": cls.CACHE_TTL_MINUTES,
            "max_size": cls.CACHE_MAX_SIZE,
            "ttl_seconds": cls.CACHE_TTL_MINUTES * 60
        }
    
    @classmethod
    def get_performance_config(cls) -> dict:
        """Get performance configuration as dictionary"""
        return {
            "max_concurrent_requests": cls.MAX_CONCURRENT_REQUESTS,
            "request_timeout_seconds": cls.REQUEST_TIMEOUT_SECONDS,
            "health_check_cache_threshold": cls.HEALTH_CHECK_CACHE_THRESHOLD,
            "health_check_response_time_threshold_ms": cls.HEALTH_CHECK_RESPONSE_TIME_THRESHOLD_MS
        }

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    LOG_LEVEL = "DEBUG"
    CACHE_TTL_MINUTES = 5  # Shorter TTL for development

class ProductionConfig(Config):
    """Production environment configuration"""
    LOG_LEVEL = "INFO"
    CACHE_TTL_MINUTES = 15  # Longer TTL for production
    CACHE_MAX_SIZE = 2000  # Larger cache for production

class TestingConfig(Config):
    """Testing environment configuration"""
    LOG_LEVEL = "DEBUG"
    ENABLE_CACHE = False  # Disable cache for testing
    CACHE_TTL_MINUTES = 1

# Configuration factory
def get_config(environment: str = None) -> Config:
    """Get configuration based on environment"""
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    return config_map.get(environment, DevelopmentConfig)

# Default configuration instance
config = get_config()
